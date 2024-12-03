from unittest.mock import MagicMock, patch

import pytest
from app.database import SalesTable
from app.models import Purchase


@pytest.fixture
def mock_client():
    # Mock the Supabase client and table
    client_mock = MagicMock()
    table_mock = MagicMock()
    client_mock.table.return_value = table_mock
    return client_mock


@pytest.fixture
def mock_sales_table(mock_client):
    # Patch the `create_client` function to return our mock client
    with patch("app.database.create_client", return_value=mock_client):
        sales_table = SalesTable("test_url", "test_key")
    return sales_table


def test_record_purchase_success(mock_sales_table, mock_client):
    # Arrange
    purchase = Purchase(
        good_id=101, customer_id="C001", amount_deducted=99.99, time=None
    )
    mock_execute = MagicMock(return_value=MagicMock(data={"id": 1}, error=None))
    mock_sales_table.table.insert.return_value.execute = mock_execute

    # Act
    result = mock_sales_table.record_purchase(purchase)

    # Assert
    mock_sales_table.table.insert.assert_called_once_with(
        purchase.model_dump(exclude={"time"})
    )
    mock_execute.assert_called_once()
    assert result == {"id": 1}


def test_record_purchase_failure(mock_sales_table, mock_client):
    # Arrange
    purchase = Purchase(
        good_id=101, customer_id="C001", amount_deducted=99.99, time=None
    )
    mock_execute = MagicMock(
        return_value=MagicMock(data=None, error=MagicMock(message="Insert error"))
    )
    mock_sales_table.table.insert.return_value.execute = mock_execute

    # Act & Assert
    with pytest.raises(Exception, match="Failed to record purchase: Insert error"):
        mock_sales_table.record_purchase(purchase)


def test_get_purchases_success(mock_sales_table, mock_client):
    # Arrange
    mock_execute = MagicMock(
        return_value=MagicMock(
            data=[
                {
                    "good_id": 101,
                    "customer_id": "C001",
                    "amount_deducted": 99.99,
                    "time": "2023-12-01T10:00:00",
                }
            ],
            error=None,
        )
    )
    mock_sales_table.table.select.return_value.execute = mock_execute

    # Act
    result = mock_sales_table.get_purchases()

    # Assert
    mock_sales_table.table.select.assert_called_once_with("*")
    mock_execute.assert_called_once()
    assert result == [
        {
            "good_id": 101,
            "customer_id": "C001",
            "amount_deducted": 99.99,
            "time": "2023-12-01T10:00:00",
        }
    ]


def test_get_purchases_no_records(mock_sales_table, mock_client):
    # Arrange
    mock_execute = MagicMock(return_value=MagicMock(data=[], error=None))
    mock_sales_table.table.select.return_value.execute = mock_execute

    # Act
    result = mock_sales_table.get_purchases()

    # Assert
    mock_sales_table.table.select.assert_called_once_with("*")
    mock_execute.assert_called_once()
    assert result == []


def test_get_purchases_failure(mock_sales_table, mock_client):
    # Arrange
    mock_execute = MagicMock(
        return_value=MagicMock(data=None, error=MagicMock(message="Select error"))
    )
    mock_sales_table.table.select.return_value.execute = mock_execute

    # Act & Assert
    with pytest.raises(Exception, match="Failed to fetch purchases: Select error"):
        mock_sales_table.get_purchases()
