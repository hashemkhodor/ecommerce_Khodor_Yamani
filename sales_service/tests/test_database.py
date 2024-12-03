import pytest
from unittest.mock import patch, MagicMock
from typing import List

# from app.models import Purchase
from app.database import record_purchase, get_purchases


@pytest.fixture
def mock_supabase_client():
    with patch('database.supabase') as mock_client:
        yield mock_client


def test_record_purchase_success(mock_supabase_client):
    """Test that record_purchase successfully records a purchase."""
    mock_response = MagicMock()
    mock_response.error = None
    mock_response.data = {'id': 1}
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

    purchase = Purchase(good_id=1, customer_id='cust123', amount_deducted=100.0)
    result = record_purchase(purchase)

    assert result == mock_response.data
    mock_supabase_client.table.assert_called_with("purchases")
    mock_supabase_client.table.return_value.insert.assert_called_with(purchase.model_dump())


def test_record_purchase_failure(mock_supabase_client):
    """Test that record_purchase raises an exception when Supabase returns an error."""
    mock_error = MagicMock()
    mock_error.message = "Database error"
    mock_response = MagicMock()
    mock_response.error = mock_error
    mock_response.data = None
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

    purchase = Purchase(good_id=1, customer_id='cust123', amount_deducted=100.0)

    with pytest.raises(Exception) as exc_info:
        record_purchase(purchase)
    assert str(exc_info.value) == f"Failed to record purchase: {mock_error.message}"


def test_get_purchases_success(mock_supabase_client):
    """Test that get_purchases returns a list of purchases when successful."""
    mock_response = MagicMock()
    mock_response.error = None
    mock_response.data = [
        {'id': 1, 'good_id': 1, 'customer_id': 'cust123', 'amount_deducted': 100.0, 'time': '2023-01-01T00:00:00Z'},
        {'id': 2, 'good_id': 2, 'customer_id': 'cust456', 'amount_deducted': 50.0, 'time': '2023-01-02T00:00:00Z'},
    ]
    mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

    result = get_purchases()

    assert result == mock_response.data
    mock_supabase_client.table.assert_called_with("purchases")
    mock_supabase_client.table.return_value.select.assert_called_with("*")


def test_get_purchases_no_data(mock_supabase_client):
    """Test that get_purchases returns an empty list when no data is found."""
    mock_response = MagicMock()
    mock_response.error = None
    mock_response.data = None
    mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

    result = get_purchases()

    assert result == []
    mock_supabase_client.table.assert_called_with("purchases")
    mock_supabase_client.table.return_value.select.assert_called_with("*")


def test_get_purchases_failure(mock_supabase_client):
    """Test that get_purchases raises an exception when Supabase returns an error."""
    mock_error = MagicMock()
    mock_error.message = "Database error"
    mock_response = MagicMock()
    mock_response.error = mock_error
    mock_response.data = None
    mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        get_purchases()
    assert str(exc_info.value) == f"Failed to fetch purchases: {mock_error.message}"
