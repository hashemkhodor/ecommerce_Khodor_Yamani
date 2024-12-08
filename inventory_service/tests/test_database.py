from unittest.mock import MagicMock, patch

import pytest
from app.database import InventoryTable
from app.models import Good, GoodUpdate
from supabase import Client


@pytest.fixture
def good_data():
    return Good(
        name="Test Product",
        category="electronics",
        price=99.99,
        description="A test product",
        count=10,
    )


@pytest.fixture
def updated_good_data():
    return GoodUpdate(
        price=89.99,
        count=15,
    )


@pytest.fixture
def inventory_table():
    with patch("app.database.create_client") as mock_create_client:
        mock_client = MagicMock(spec=Client)
        mock_create_client.return_value = mock_client
        inv_table = InventoryTable(url="http://test-url.com", key="test-key")
        return inv_table, mock_client


def test_add_good_to_db_success(inventory_table, good_data):
    inv_table, mock_client = inventory_table
    # Mock the insert response
    mock_response = MagicMock()
    mock_response.data = [good_data.model_dump()]
    mock_response.error = None
    mock_client.table.return_value.insert.return_value.execute.return_value = (
        mock_response
    )

    result = inv_table.add_good_to_db(good_data)
    assert result == [good_data.model_dump()]
    mock_client.table.assert_called_with("inventory")
    mock_client.table.return_value.insert.assert_called_with(good_data.model_dump())


def test_add_good_to_db_failure(inventory_table, good_data):
    inv_table, mock_client = inventory_table
    # Mock the insert response with an error
    mock_response = MagicMock()
    mock_response.data = None
    mock_response.error = MagicMock()
    mock_response.error.message = "Insert failed"
    mock_client.table.return_value.insert.return_value.execute.return_value = (
        mock_response
    )

    with pytest.raises(Exception) as exc_info:
        inv_table.add_good_to_db(good_data)
    assert str(exc_info.value) == "Failed to add good: Insert failed"


def test_update_good_in_db_failure(inventory_table, updated_good_data):
    inv_table, mock_client = inventory_table
    good_id = 1
    # Mock the update response with an error
    mock_response = MagicMock()
    mock_response.data = None
    mock_response.error = MagicMock()
    mock_response.error.message = "Update failed"
    mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
        mock_response
    )

    with pytest.raises(Exception) as exc_info:
        inv_table.update_good_in_db(good_id, updated_good_data)
    assert str(exc_info.value) == "Failed to update good: Update failed"


def test_get_good_from_db_success(inventory_table, good_data):
    inv_table, mock_client = inventory_table
    good_id = 1
    # Mock the select response
    mock_response = MagicMock()
    mock_response.data = [good_data.model_dump()]
    mock_response.error = None
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_response
    )

    result = inv_table.get_good_from_db(good_id)
    assert result == good_data.model_dump()
    mock_client.table.assert_called_with("inventory")
    mock_client.table.return_value.select.assert_called_with("*")
    mock_client.table.return_value.select.return_value.eq.assert_called_with(
        "id", good_id
    )


def test_get_good_from_db_failure(inventory_table):
    inv_table, mock_client = inventory_table
    good_id = 1
    # Mock the select response with an error
    mock_response = MagicMock()
    mock_response.data = None
    mock_response.error = MagicMock()
    mock_response.error.message = "Fetch failed"
    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_response
    )

    with pytest.raises(Exception) as exc_info:
        inv_table.get_good_from_db(good_id)
    assert str(exc_info.value) == "Failed to fetch good: Fetch failed"


def test_deduct_good_from_db_success(inventory_table, good_data):
    inv_table, mock_client = inventory_table
    good_id = 1
    initial_count = good_data.count
    # Mock the select response to get the product
    mock_select_response = MagicMock()
    mock_select_response.data = [good_data.model_dump()]
    mock_select_response.error = None
    # Mock the update response
    mock_update_response = MagicMock()
    mock_update_response.data = [{"count": initial_count - 1}]
    mock_update_response.error = None

    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_select_response
    )
    mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
        mock_update_response
    )

    result = inv_table.deduct_good_from_db(good_id)
    assert result == [{"count": initial_count - 1}]
    mock_client.table.assert_called_with("inventory")
    mock_client.table.return_value.select.assert_called_with("*")
    mock_client.table.return_value.select.return_value.eq.assert_called_with(
        "id", good_id
    )
    mock_client.table.return_value.update.assert_called_with(
        {"count": initial_count - 1}
    )
    mock_client.table.return_value.update.return_value.eq.assert_called_with(
        "id", good_id
    )


def test_deduct_good_from_db_no_stock(inventory_table, good_data):
    inv_table, mock_client = inventory_table
    good_id = 1
    good_data.count = 0
    # Mock the select response to get the product with zero count
    mock_select_response = MagicMock()
    mock_select_response.data = [good_data.model_dump()]
    mock_select_response.error = None

    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_select_response
    )

    with pytest.raises(ValueError) as exc_info:
        inv_table.deduct_good_from_db(good_id)
    assert str(exc_info.value) == "Product count less than 0"


def test_deduct_good_from_db_failure(inventory_table, good_data):
    inv_table, mock_client = inventory_table
    good_id = 1
    # Mock the select response
    mock_select_response = MagicMock()
    mock_select_response.data = [good_data.model_dump()]
    mock_select_response.error = None
    # Mock the update response with an error
    mock_update_response = MagicMock()
    mock_update_response.data = None
    mock_update_response.error = MagicMock()
    mock_update_response.error.message = "Update failed"

    mock_client.table.return_value.select.return_value.eq.return_value.execute.return_value = (
        mock_select_response
    )
    mock_client.table.return_value.update.return_value.eq.return_value.execute.return_value = (
        mock_update_response
    )

    with pytest.raises(Exception) as exc_info:
        inv_table.deduct_good_from_db(good_id)
    assert str(exc_info.value) == "Failed to deduct inventory: Update failed"
