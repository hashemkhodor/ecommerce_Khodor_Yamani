import pytest
from app.models import Purchase  # Replace with the correct import path if different
from pydantic import ValidationError


def test_purchase_creation():
    """Test successful creation of a Purchase instance with valid data."""
    data = {"good_id": 1, "customer_id": "cust123", "amount_deducted": 100.0}
    purchase = Purchase(**data)
    assert purchase.good_id == data["good_id"]
    assert purchase.customer_id == data["customer_id"]
    assert purchase.amount_deducted == data["amount_deducted"]


def test_purchase_negative_amount():
    """Test that creating a Purchase with a negative amount_deducted raises a ValidationError."""
    data = {"good_id": 1, "customer_id": "cust123", "amount_deducted": -50.0}
    with pytest.raises(ValidationError) as exc_info:
        Purchase(**data)
    errors = exc_info.value.errors()
    assert errors[0]["loc"] == ("amount_deducted",)
    assert "Input should be greater than or equal to 0" in errors[0]["msg"]


@pytest.mark.parametrize("missing_field", ["good_id", "customer_id", "amount_deducted"])
def test_purchase_missing_fields(missing_field):
    """Test that missing required fields raise a ValidationError."""
    data = {"good_id": 1, "customer_id": "cust123", "amount_deducted": 100.0}
    data.pop(missing_field)
    with pytest.raises(ValidationError) as exc_info:
        Purchase(**data)
    errors = exc_info.value.errors()
    assert any(error["loc"][0] == missing_field for error in errors)


def test_purchase_zero_amount():
    """Test that amount_deducted can be zero."""
    data = {"good_id": 1, "customer_id": "cust123", "amount_deducted": 0.0}
    purchase = Purchase(**data)
    assert purchase.amount_deducted == 0.0


def test_purchase_invalid_good_id_type():
    """Test that providing an invalid type for good_id raises a ValidationError."""
    data = {"good_id": "invalid_id", "customer_id": "cust123", "amount_deducted": 100.0}
    with pytest.raises(ValidationError):
        Purchase(**data)
