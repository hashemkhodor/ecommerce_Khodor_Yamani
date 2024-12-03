from unittest.mock import MagicMock, patch

import pytest
from app.models import Good, GoodUpdate
from app.service import add_good, deduct_good, get_good, update_good


@pytest.fixture
def good_data():
    return {
        "name": "Test Product",
        "category": "electronics",
        "price": 99.99,
        "description": "A test product",
        "count": 10,
    }


@pytest.fixture
def updated_good_data():
    return {
        "price": 89.99,
        "count": 15,
    }


def test_add_good_success(good_data):
    with patch("app.service.db_inv.add_good_to_db") as mock_add_good_to_db:
        mock_add_good_to_db.return_value = None

        result = add_good(Good(**good_data))
        assert result == {"message": "Good added successfully"}
        mock_add_good_to_db.assert_called_once_with(Good(**good_data))


def test_add_good_failure(good_data):
    with patch("app.service.db_inv.add_good_to_db") as mock_add_good_to_db:
        mock_add_good_to_db.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            add_good(Good(**good_data))
        mock_add_good_to_db.assert_called_once_with(Good(**good_data))


def test_update_good_success(good_data, updated_good_data):
    good_id = 1
    existing_good = {**good_data, "id": good_id}
    updated_good = {**good_data, **updated_good_data}

    with patch("app.service.db_inv.get_good_from_db") as mock_get_good_from_db, patch(
        "app.service.db_inv.update_good_in_db"
    ) as mock_update_good_in_db:
        mock_get_good_from_db.return_value = existing_good
        mock_update_good_in_db.return_value = None

        result = update_good(good_id, GoodUpdate(**updated_good_data))
        assert result == {"message": "Good updated successfully"}
        mock_get_good_from_db.assert_called_once_with(good_id)
        mock_update_good_in_db.assert_called_once_with(good_id, updated_good)


def test_update_good_not_found(updated_good_data):
    good_id = 1

    with patch("app.service.db_inv.get_good_from_db") as mock_get_good_from_db, patch(
        "app.service.db_inv.update_good_in_db"
    ) as mock_update_good_in_db:
        mock_get_good_from_db.return_value = None

        with pytest.raises(ValueError, match="Good not found"):
            update_good(good_id, GoodUpdate(**updated_good_data))
        mock_get_good_from_db.assert_called_once_with(good_id)
        mock_update_good_in_db.assert_not_called()


def test_get_good_success(good_data):
    good_id = 1
    good_data_with_id = {**good_data, "id": good_id}

    with patch("app.service.db_inv.get_good_from_db") as mock_get_good_from_db:
        mock_get_good_from_db.return_value = good_data_with_id

        result = get_good(good_id)
        assert result == good_data_with_id
        mock_get_good_from_db.assert_called_once_with(good_id)


def test_get_good_not_found():
    good_id = 1

    with patch("app.service.db_inv.get_good_from_db") as mock_get_good_from_db:
        mock_get_good_from_db.return_value = None

        with pytest.raises(ValueError, match="Good not found"):
            get_good(good_id)
        mock_get_good_from_db.assert_called_once_with(good_id)


def test_deduct_good_success():
    good_id = 1

    with patch("app.service.db_inv.deduct_good_from_db") as mock_deduct_good_from_db:
        mock_deduct_good_from_db.return_value = None

        result = deduct_good(good_id)
        assert result == {"message": "Stock deducted successfully"}
        mock_deduct_good_from_db.assert_called_once_with(good_id)


def test_deduct_good_insufficient_stock():
    good_id = 1

    with patch("app.service.db_inv.deduct_good_from_db") as mock_deduct_good_from_db:
        mock_deduct_good_from_db.side_effect = ValueError("Insufficient stock")

        with pytest.raises(ValueError, match="Insufficient stock"):
            deduct_good(good_id)
        mock_deduct_good_from_db.assert_called_once_with(good_id)
