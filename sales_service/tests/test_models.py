import pytest
from datetime import datetime, timezone, timedelta
from pydantic import ValidationError
from app.models import Purchase  # Replace with the correct import path if different

def test_purchase_creation():
    """Test successful creation of a Purchase instance with valid data."""
    data = {
        'good_id': 1,
        'customer_id': 'cust123',
        'amount_deducted': 100.0
    }
    purchase = Purchase(**data)
    assert purchase.good_id == data['good_id']
    assert purchase.customer_id == data['customer_id']
    assert purchase.amount_deducted == data['amount_deducted']
    assert isinstance(purchase.time, datetime)

def test_purchase_negative_amount():
    """Test that creating a Purchase with a negative amount_deducted raises a ValidationError."""
    data = {
        'good_id': 1,
        'customer_id': 'cust123',
        'amount_deducted': -50.0
    }
    with pytest.raises(ValidationError) as exc_info:
        Purchase(**data)
    errors = exc_info.value.errors()
    assert errors[0]['loc'] == ('amount_deducted',)
    assert 'Input should be greater than or equal to 0' in errors[0]['msg']

def test_purchase_default_time():
    """Test that the default time is set to the current UTC time."""
    before_creation = datetime.now(timezone.utc)
    data = {
        'good_id': 1,
        'customer_id': 'cust123',
        'amount_deducted': 100.0
    }
    purchase = Purchase(**data)
    after_creation = datetime.now(timezone.utc)
    assert before_creation <= purchase.time <= after_creation

def test_purchase_custom_time():
    """Test that a custom time can be assigned to the Purchase instance."""
    custom_time = datetime(2023, 1, 1, tzinfo=timezone.utc)
    data = {
        'good_id': 1,
        'customer_id': 'cust123',
        'amount_deducted': 100.0,
        'time': custom_time
    }
    purchase = Purchase(**data)
    assert purchase.time == custom_time

@pytest.mark.parametrize("missing_field", ['good_id', 'customer_id', 'amount_deducted'])
def test_purchase_missing_fields(missing_field):
    """Test that missing required fields raise a ValidationError."""
    data = {
        'good_id': 1,
        'customer_id': 'cust123',
        'amount_deducted': 100.0
    }
    data.pop(missing_field)
    with pytest.raises(ValidationError) as exc_info:
        Purchase(**data)
    errors = exc_info.value.errors()
    assert any(error['loc'][0] == missing_field for error in errors)

def test_purchase_zero_amount():
    """Test that amount_deducted can be zero."""
    data = {
        'good_id': 1,
        'customer_id': 'cust123',
        'amount_deducted': 0.0
    }
    purchase = Purchase(**data)
    assert purchase.amount_deducted == 0.0

def test_purchase_time_timezone():
    """Test that the time field is timezone-aware and set to UTC."""
    data = {
        'good_id': 1,
        'customer_id': 'cust123',
        'amount_deducted': 100.0
    }
    purchase = Purchase(**data)
    assert purchase.time.tzinfo == timezone.utc

def test_purchase_invalid_good_id_type():
    """Test that providing an invalid type for good_id raises a ValidationError."""
    data = {
        'good_id': 'invalid_id',
        'customer_id': 'cust123',
        'amount_deducted': 100.0
    }
    with pytest.raises(ValidationError):
        Purchase(**data)
