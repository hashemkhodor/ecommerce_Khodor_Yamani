
import pytest
from unittest.mock import MagicMock, patch
from starlette import status

from app.models import ReviewTable
from app.schemas import Review


@pytest.fixture
def review_table():
    with patch('app.models.create_client') as mock_create_client:
        mock_client = MagicMock()
        mock_create_client.return_value = mock_client
        # Initialize ReviewTable with mocked client
        table = ReviewTable(url='mock_url', key='mock_key')
        table.client = mock_client
        yield table

# Test cases for customer_and_item_exist method
def test_customer_and_item_exist_both_exist(review_table):
    # Mock the customer exists
    review_table.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{}]
    # Mock the item exists
    review_table.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [{}]

    status_code = review_table.customer_and_item_exist('customer1', 1)
    assert status_code == status.HTTP_200_OK

def test_customer_and_item_exist_customer_missing(review_table):
    # Mock the customer does not exist
    review_table.client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
    # The item check should not matter in this case
    status_code = review_table.customer_and_item_exist('customer1', 1)
    assert status_code == status.HTTP_400_BAD_REQUEST

def test_customer_and_item_exist_item_missing(review_table):
    # Mock the customer exists
    mock_select = MagicMock()
    mock_select.execute.return_value.data = [{}]
    review_table.client.table.return_value.select.return_value.eq.return_value = mock_select

    # Mock the item does not exist
    mock_select_item = MagicMock()
    mock_select_item.execute.return_value.data = []
    review_table.client.table.return_value.select.return_value.eq.return_value = mock_select_item

    status_code = review_table.customer_and_item_exist('customer1', 1)
    assert status_code == status.HTTP_400_BAD_REQUEST

def test_customer_and_item_exist_exception(review_table):
    # Mock an exception during customer check
    review_table.client.table.return_value.select.return_value.eq.return_value.execute.side_effect = Exception("Database error")
    status_code = review_table.customer_and_item_exist('customer1', 1)
    assert status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

# Test cases for submit_review method
def test_submit_review_success(review_table):
    review = Review(
        customer_id="customer1",
        item_id=1,
        rating=5,
        comment="Great product!",
        time=None,
        flagged="needs_approval",
    )
    # Mock the insert operation returning data
    mock_insert = MagicMock()
    mock_insert.execute.return_value.data = [review.model_dump()]
    review_table.table.insert.return_value = mock_insert

    result = review_table.submit_review(review)
    assert result == [review]
    review_table.table.insert.assert_called_once_with(review.model_dump(exclude={"time"}))

def test_submit_review_failure(review_table):
    review = Review(
        customer_id="customer1",
        item_id=1,
        rating=5,
        comment="Great product!",
        time=None,
        flagged="needs_approval",
    )
    # Mock the insert operation returning no data
    mock_insert = MagicMock()
    mock_insert.execute.return_value.data = []
    review_table.table.insert.return_value = mock_insert

    result = review_table.submit_review(review)
    assert result == []
    review_table.table.insert.assert_called_once_with(review.model_dump(exclude={"time"}))

def test_submit_review_exception(review_table):
    review = Review(
        customer_id="customer1",
        item_id=1,
        rating=5,
        comment="Great product!",
        time=None,
        flagged="needs_approval",
    )
    # Mock an exception during insert
    review_table.table.insert.side_effect = Exception("Database error")
    result = review_table.submit_review(review)
    assert result is None

# Test cases for get_reviews method
def test_get_reviews_success(review_table):
    # Mock data to be returned by execute()
    review_data = [
        {
            "customer_id": "customer1",
            "item_id": 1,
            "rating": 5,
            "comment": "Great product!",
            "time": None,
            "flagged": "approved",
        }
    ]

    # Create a mock for the query builder
    mock_query = MagicMock()
    # Configure the execute() method to return the desired data
    mock_query.execute.return_value.data = review_data
    # Configure the eq() method to return the same mock, so we can chain calls
    mock_query.eq.return_value = mock_query
    # Configure the select("*") method to return the mock_query
    review_table.table.select.return_value = mock_query

    result = review_table.get_reviews(customer_id="customer1")
    assert len(result) == 1
    assert result[0].customer_id == "customer1"


def test_get_reviews_no_data(review_table):
    # Mock the select operation returning no data
    mock_select = MagicMock()
    mock_select.execute.return_value.data = []
    review_table.table.select.return_value = mock_select

    result = review_table.get_reviews(customer_id="customer1")
    assert result == []

def test_get_reviews_exception(review_table):
    # Mock an exception during select
    review_table.table.select.side_effect = Exception("Database error")
    result = review_table.get_reviews(customer_id="customer1")
    assert result is None

# Test cases for update_review method
def test_update_review_success(review_table):
    review = Review(
        customer_id="customer1",
        item_id=1,
        rating=4,
        comment="Updated comment",
        time=None,
        flagged="approved",
    )
    # Mock the update operation returning data
    mock_update = MagicMock()
    mock_update.execute.return_value.data = [review.model_dump()]
    review_table.table.update.return_value.eq.return_value.eq.return_value = mock_update

    result = review_table.update_review(review)
    assert result == [review]
    review_table.table.update.assert_called_once_with(review.model_dump(exclude={"customer_id", "item_id"}))

def test_update_review_failure(review_table):
    review = Review(
        customer_id="customer1",
        item_id=1,
        rating=4,
        comment="Updated comment",
        time=None,
        flagged="approved",
    )
    # Mock the update operation returning no data
    mock_update = MagicMock()
    mock_update.execute.return_value.data = []
    review_table.table.update.return_value.eq.return_value.eq.return_value = mock_update

    result = review_table.update_review(review)
    assert result == []
    review_table.table.update.assert_called_once_with(review.model_dump(exclude={"customer_id", "item_id"}))

def test_update_review_exception(review_table):
    review = Review(
        customer_id="customer1",
        item_id=1,
        rating=4,
        comment="Updated comment",
        time=None,
        flagged="approved",
    )
    # Mock an exception during update
    review_table.table.update.side_effect = Exception("Database error")
    result = review_table.update_review(review)
    assert result is None

# Test cases for delete_review method
def test_delete_review_success(review_table):
    # Mock the delete operation returning data
    mock_delete = MagicMock()
    mock_delete.execute.return_value.data = [{}]
    review_table.table.delete.return_value.eq.return_value.eq.return_value = mock_delete

    result = review_table.delete_review(item_id=1, customer_id="customer1")
    assert result is True

def test_delete_review_failure(review_table):
    # Mock the delete operation returning no data
    mock_delete = MagicMock()
    mock_delete.execute.return_value.data = []
    review_table.table.delete.return_value.eq.return_value.eq.return_value = mock_delete

    result = review_table.delete_review(item_id=1, customer_id="customer1")
    assert result is False

def test_delete_review_exception(review_table):
    # Mock an exception during delete
    review_table.table.delete.side_effect = Exception("Database error")
    result = review_table.delete_review(item_id=1, customer_id="customer1")
    assert result is None

# Test cases for get_review, get_item_reviews, get_customer_reviews methods
def test_get_review(review_table):
    with patch.object(review_table, 'get_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = ["review1"]
        result = review_table.get_review(item_id=1, customer_id="customer1")
        assert result == ["review1"]
        mock_get_reviews.assert_called_once_with(item_id=1, customer_id="customer1")

def test_get_item_reviews(review_table):
    with patch.object(review_table, 'get_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = ["review1", "review2"]
        result = review_table.get_item_reviews(item_id=1)
        assert result == ["review1", "review2"]
        mock_get_reviews.assert_called_once_with(item_id=1)

def test_get_customer_reviews(review_table):
    with patch.object(review_table, 'get_reviews') as mock_get_reviews:
        mock_get_reviews.return_value = ["review1", "review2"]
        result = review_table.get_customer_reviews(customer_id="customer1")
        assert result == ["review1", "review2"]
        mock_get_reviews.assert_called_once_with(customer_id="customer1")
