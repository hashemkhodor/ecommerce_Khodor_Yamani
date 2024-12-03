from unittest.mock import MagicMock, patch

import pytest
from app.service import (
    deduct_inventory,
    deduct_wallet_balance,
    fetch_good_details,
    get_purchases,
    process_purchase,
)
from fastapi import HTTPException

# Constants used in the service module
INVENTORY_SERVICE_URL = "http://127.0.0.1:8002/api/v1/inventory"
CUSTOMER_SERVICE_URL = "http://127.0.0.1:8001/api/v1/customer"


# Tests for fetch_good_details function
def test_fetch_good_details_success():
    # Arrange
    good_id = 123
    expected_response = {"id": good_id, "name": "Test Good", "price": 10.0}

    with patch("app.service.httpx.Client") as mock_client_class:
        mock_client_instance = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response
        mock_client_instance.get.return_value = mock_response

        # Act
        result = fetch_good_details(good_id)

        # Assert
        mock_client_instance.get.assert_called_once_with(
            f"{INVENTORY_SERVICE_URL}/{good_id}"
        )
        assert result == expected_response


def test_fetch_good_details_not_found():
    # Arrange
    good_id = 123

    with patch("app.service.httpx.Client") as mock_client_class:
        mock_client_instance = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client_instance.get.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match=f"Good with ID '{good_id}' not found"):
            fetch_good_details(good_id)


def test_fetch_good_details_error():
    # Arrange
    good_id = 123

    with patch("app.service.httpx.Client") as mock_client_class:
        mock_client_instance = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client_instance.get.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to fetch good details"):
            fetch_good_details(good_id)


# Tests for deduct_wallet_balance function
def test_deduct_wallet_balance_success():
    # Arrange
    customer_username = "testuser"
    amount = 10.0
    expected_response = {"message": "Balance deducted"}

    with patch("app.service.httpx.Client") as mock_client_class:
        mock_client_instance = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response
        mock_client_instance.put.return_value = mock_response

        # Act
        result = deduct_wallet_balance(customer_username, amount)

        # Assert
        mock_client_instance.put.assert_called_once_with(
            f"{CUSTOMER_SERVICE_URL}/wallet/{customer_username}/deduct", json=amount
        )
        assert result == expected_response


def test_deduct_wallet_balance_customer_not_found():
    # Arrange
    customer_username = "testuser"
    amount = 10.0

    with patch("app.service.httpx.Client") as mock_client_class:
        mock_client_instance = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client_instance.put.return_value = mock_response

        # Act & Assert
        with pytest.raises(
            ValueError,
            match=f"Customer '{customer_username}' not found in the database",
        ):
            deduct_wallet_balance(customer_username, amount)


def test_deduct_wallet_balance_insufficient_funds():
    # Arrange
    customer_username = "testuser"
    amount = 10.0

    with patch("app.service.httpx.Client") as mock_client_class:
        mock_client_instance = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_client_instance.put.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match="Amount not enough"):
            deduct_wallet_balance(customer_username, amount)


def test_deduct_wallet_balance_error():
    # Arrange
    customer_username = "testuser"
    amount = 10.0

    with patch("app.service.httpx.Client") as mock_client_class:
        mock_client_instance = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client_instance.put.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to deduct wallet balance"):
            deduct_wallet_balance(customer_username, amount)


# Tests for deduct_inventory function
def test_deduct_inventory_success():
    # Arrange
    good_id = 123
    expected_response = {"message": "Inventory deducted"}

    with patch("app.service.httpx.Client") as mock_client_class:
        mock_client_instance = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_response
        mock_client_instance.put.return_value = mock_response

        # Act
        result = deduct_inventory(good_id)

        # Assert
        mock_client_instance.put.assert_called_once_with(
            f"{INVENTORY_SERVICE_URL}/deduct/{good_id}"
        )
        assert result == expected_response


def test_deduct_inventory_not_found():
    # Arrange
    good_id = 123

    with patch("app.service.httpx.Client") as mock_client_class:
        mock_client_instance = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_client_instance.put.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match=f"Good with ID '{good_id}' not found"):
            deduct_inventory(good_id)


def test_deduct_inventory_stock_zero():
    # Arrange
    good_id = 123

    with patch("app.service.httpx.Client") as mock_client_class:
        mock_client_instance = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_client_instance.put.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match="Stock already zero"):
            deduct_inventory(good_id)


def test_deduct_inventory_error():
    # Arrange
    good_id = 123

    with patch("app.service.httpx.Client") as mock_client_class:
        mock_client_instance = mock_client_class.return_value.__enter__.return_value
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_client_instance.put.return_value = mock_response

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to deduct inventory"):
            deduct_inventory(good_id)


# Tests for process_purchase function
def test_process_purchase_success():
    # Arrange
    customer_username = "testuser"
    good_id = 123
    price = 10.0
    good_details = {"id": good_id, "name": "Test Good", "price": price}

    with patch("app.service.fetch_good_details") as mock_fetch_good_details, patch(
        "app.service.deduct_wallet_balance"
    ) as mock_deduct_wallet_balance, patch(
        "app.service.deduct_inventory"
    ) as mock_deduct_inventory, patch(
        "app.service.db_sale"
    ) as mock_db_sale:

        mock_fetch_good_details.return_value = good_details
        mock_deduct_wallet_balance.return_value = {"message": "Balance deducted"}
        mock_deduct_inventory.return_value = {"message": "Inventory deducted"}
        mock_db_sale.record_purchase.return_value = None

        # Act
        result = process_purchase(customer_username, good_id)

        # Assert
        mock_fetch_good_details.assert_called_once_with(good_id)
        mock_deduct_wallet_balance.assert_called_once_with(customer_username, price)
        mock_deduct_inventory.assert_called_once_with(good_id)
        mock_db_sale.record_purchase.assert_called_once()
        assert result == {"message": "Purchase successful"}


def test_process_purchase_fetch_good_details_error():
    # Arrange
    customer_username = "testuser"
    good_id = 123

    with patch("app.service.fetch_good_details") as mock_fetch_good_details, patch(
        "app.service.logger"
    ) as mock_logger:

        mock_fetch_good_details.side_effect = ValueError("Good not found")

        # Act & Assert
        with pytest.raises(ValueError, match="Good not found"):
            process_purchase(customer_username, good_id)

        mock_fetch_good_details.assert_called_once_with(good_id)
        mock_logger.info.assert_called_with(
            f"Processing purchase for {customer_username} and good {good_id}"
        )


def test_process_purchase_deduct_wallet_balance_error():
    # Arrange
    customer_username = "testuser"
    good_id = 123
    price = 10.0
    good_details = {"id": good_id, "name": "Test Good", "price": price}

    with patch("app.service.fetch_good_details") as mock_fetch_good_details, patch(
        "app.service.deduct_wallet_balance"
    ) as mock_deduct_wallet_balance:

        mock_fetch_good_details.return_value = good_details
        mock_deduct_wallet_balance.side_effect = ValueError("Insufficient funds")

        # Act & Assert
        with pytest.raises(ValueError, match="Insufficient funds"):
            process_purchase(customer_username, good_id)

        mock_fetch_good_details.assert_called_once_with(good_id)
        mock_deduct_wallet_balance.assert_called_once_with(customer_username, price)


def test_process_purchase_deduct_inventory_error():
    # Arrange
    customer_username = "testuser"
    good_id = 123
    price = 10.0
    good_details = {"id": good_id, "name": "Test Good", "price": price}

    with patch("app.service.fetch_good_details") as mock_fetch_good_details, patch(
        "app.service.deduct_wallet_balance"
    ) as mock_deduct_wallet_balance, patch(
        "app.service.deduct_inventory"
    ) as mock_deduct_inventory:

        mock_fetch_good_details.return_value = good_details
        mock_deduct_wallet_balance.return_value = {"message": "Balance deducted"}
        mock_deduct_inventory.side_effect = ValueError("Stock already zero")

        # Act & Assert
        with pytest.raises(ValueError, match="Stock already zero"):
            process_purchase(customer_username, good_id)

        mock_fetch_good_details.assert_called_once_with(good_id)
        mock_deduct_wallet_balance.assert_called_once_with(customer_username, price)
        mock_deduct_inventory.assert_called_once_with(good_id)


# Tests for get_purchases function
def test_get_purchases_success():
    # Arrange
    purchases = [
        {
            "id": 1,
            "good_id": 123,
            "customer_id": "testuser",
            "amount_deducted": 10.0,
            "time": "2023-12-01T10:00:00",
        }
    ]
    expected_result = [
        {
            "id": 1,
            "good_id": 123,
            "customer_id": "testuser",
            "amount_deducted": 10.0,
            "time": "2023-12-01T10:00:00",
        }
    ]
    with patch("app.service.db_sale") as mock_db_sale:
        mock_db_sale.get_purchases.return_value = purchases

        # Act
        result = get_purchases()

        # Assert
        mock_db_sale.get_purchases.assert_called_once()
        assert result == expected_result


def test_get_purchases_failure():
    # Arrange
    with patch("app.service.db_sale") as mock_db_sale, patch(
        "app.service.logger"
    ) as mock_logger:

        mock_db_sale.get_purchases.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            get_purchases()

        mock_db_sale.get_purchases.assert_called_once()
        mock_logger.exception.assert_called_once()
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Database error"
