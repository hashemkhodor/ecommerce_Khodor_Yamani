import pytest
from app.models import Category, Good, GoodUpdate
from pydantic import ValidationError


def test_good_valid_data():
    good = Good(
        name="Laptop",
        category="electronics",
        price=999.99,
        description="High-end gaming laptop",
        count=10,
    )
    assert good.name == "Laptop"
    assert good.category == "electronics"
    assert good.price == 999.99
    assert good.description == "High-end gaming laptop"
    assert good.count == 10


def test_good_invalid_name_length():
    with pytest.raises(ValidationError):
        Good(
            name="x" * 101,  # Exceeds 100 characters
            category="electronics",
            price=999.99,
            description="Valid description",
            count=10,
        )


def test_good_invalid_category():
    with pytest.raises(ValidationError):
        Good(
            name="Laptop",
            category="invalid_category",  # Not in allowed categories
            price=999.99,
            description="Valid description",
            count=10,
        )


def test_good_invalid_price():
    with pytest.raises(ValidationError):
        Good(
            name="Laptop",
            category="electronics",
            price=-10.0,  # Price must be greater than 0
            description="Valid description",
            count=10,
        )


def test_good_invalid_description_length():
    with pytest.raises(ValidationError):
        Good(
            name="Laptop",
            category="electronics",
            price=999.99,
            description="x" * 256,  # Exceeds 255 characters
            count=10,
        )


def test_good_invalid_count():
    with pytest.raises(ValidationError):
        Good(
            name="Laptop",
            category="electronics",
            price=999.99,
            description="Valid description",
            count=-1,  # Count must be non-negative
        )


def test_good_update_partial_update():
    update = GoodUpdate(price=199.99, count=20)
    assert update.price == 199.99
    assert update.count == 20


def test_good_update_invalid_name_length():
    with pytest.raises(ValidationError):
        GoodUpdate(name="x" * 101)  # Exceeds 100 characters


def test_good_update_invalid_category():
    with pytest.raises(ValidationError):
        GoodUpdate(category="invalid_category")  # Not in allowed categories


def test_good_update_invalid_price():
    with pytest.raises(ValidationError):
        GoodUpdate(price=0)  # Price must be greater than 0


def test_good_update_invalid_count():
    with pytest.raises(ValidationError):
        GoodUpdate(count=-5)  # Count must be non-negative


def test_good_update_no_fields():
    update = GoodUpdate()  # All fields are optional
    assert update.model_dump(exclude_unset=True) == {}


def test_category_enum():
    assert Category.FOOD == "food"
    assert Category.CLOTHES == "clothes"
    assert Category.ACCESSORIES == "accessories"
    assert Category.ELECTRONICS == "electronics"
