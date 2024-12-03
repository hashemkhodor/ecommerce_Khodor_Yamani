
import pytest
from unittest.mock import patch, MagicMock
from app.models import CustomerTable
from app.schemas import Customer, Wallet
from supabase import Client
from postgrest import SyncRequestBuilder
from loguru import logger


# Helper function to create a mock Supabase client
def create_mock_supabase_client():
    mock_client = MagicMock(spec=Client)
    mock_table_customer = MagicMock(spec=SyncRequestBuilder)
    mock_table_wallet = MagicMock(spec=SyncRequestBuilder)

    def table_side_effect(table_name):
        if table_name == "customer":
            return mock_table_customer
        elif table_name == "wallet":
            return mock_table_wallet
        else:
            raise ValueError(f"Unknown table {table_name}")

    mock_client.table.side_effect = table_side_effect
    return mock_client, mock_table_customer, mock_table_wallet


@patch('app.models.create_client')
def test_customer_table_init(mock_create_client):
    # Arrange
    mock_client = MagicMock(spec=Client)
    mock_create_client.return_value = mock_client
    url = 'http://example.com'
    key = 'fake_key'

    # Act
    customer_table = CustomerTable(url, key)

    # Assert
    mock_create_client.assert_called_once_with(url, key)
    assert customer_table.client == mock_client
    assert isinstance(customer_table.table, MagicMock)


@patch('app.models.create_client')
def test_create_customer_success(mock_create_client):
    # Arrange
    mock_client, mock_table_customer, mock_table_wallet = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    customer = Customer(
        name='John Doe',
        username='johndoe',
        password='password123',
        age=30,
        address='123 Main St',
        gender=True,
        marital_status='single',
        role='customer'
    )

    # Mock the insert method for customer
    mock_table_customer.insert.return_value.execute.return_value.data = [customer.model_dump()]
    # Mock the insert method for wallet
    mock_table_wallet.insert.return_value.execute.return_value.data = [{'customer_id': customer.username, 'amount': 0.0}]

    # Act
    result = customer_table.create_customer(customer)

    # Assert
    assert result == True
    mock_table_customer.insert.assert_called_once_with(customer.model_dump())
    mock_table_wallet.insert.assert_called_once_with({'customer_id': customer.username, 'amount': 0.0})


@patch('app.models.create_client')
def test_create_customer_failure(mock_create_client):
    # Arrange
    mock_client, mock_table_customer, mock_table_wallet = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    customer = Customer(
        name='Jane Doe',
        username='janedoe',
        password='password123',
        age=28,
        address='456 Main St',
        gender=False,
        marital_status='married',
        role='customer'
    )

    # Mock the insert method for customer to fail (no data returned)
    mock_table_customer.insert.return_value.execute.return_value.data = None

    # Act
    result = customer_table.create_customer(customer)

    # Assert
    assert result == False
    mock_table_customer.insert.assert_called_once_with(customer.model_dump())
    mock_table_wallet.insert.assert_not_called()


@patch('app.models.create_client')
def test_create_customer_exception(mock_create_client):
    # Arrange
    mock_client, mock_table_customer, mock_table_wallet = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    customer = Customer(
        name='Error User',
        username='erroruser',
        password='password123',
        age=40,
        address='789 Main St',
        gender=True,
        marital_status='divorced',
        role='customer'
    )

    # Mock the insert method for customer to raise an exception
    mock_table_customer.insert.return_value.execute.side_effect = Exception('Database Error')

    # Act
    result = customer_table.create_customer(customer)

    # Assert
    assert result is None
    mock_table_customer.insert.assert_called_once_with(customer.model_dump())
    mock_table_wallet.insert.assert_not_called()


@patch('app.models.create_client')
def test_get_users_success(mock_create_client):
    # Arrange
    mock_client, mock_table_customer, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    customer_data = [
        {
            'name': 'John Doe',
            'username': 'johndoe',
            'password': 'password123',
            'age': 30,
            'address': '123 Main St',
            'gender': True,
            'marital_status': 'single',
            'role': 'customer'
        }
    ]

    # Mock the select and filter methods
    mock_query = MagicMock()
    mock_table_customer.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.execute.return_value.data = customer_data

    # Act
    result = customer_table.get_users(role='customer')

    # Assert
    assert result == [Customer.model_validate(customer_data[0])]
    mock_table_customer.select.assert_called_once_with('*')
    mock_query.eq.assert_called_once_with('role', 'customer')
    mock_query.execute.assert_called_once()


@patch('app.models.create_client')
def test_get_users_no_users(mock_create_client):
    # Arrange
    mock_client, mock_table_customer, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    # Mock the select and filter methods
    mock_query = MagicMock()
    mock_table_customer.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.execute.return_value.data = []

    # Act
    result = customer_table.get_users(role='admin')

    # Assert
    assert result == []
    mock_table_customer.select.assert_called_once_with('*')
    mock_query.eq.assert_called_once_with('role', 'admin')
    mock_query.execute.assert_called_once()


@patch('app.models.create_client')
def test_get_users_exception(mock_create_client):
    # Arrange
    mock_client, mock_table_customer, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    # Mock the select method to raise an exception
    mock_table_customer.select.side_effect = Exception('Database Error')

    # Act
    result = customer_table.get_users(role='customer')

    # Assert
    assert result is None
    mock_table_customer.select.assert_called_once_with('*')


@patch('app.models.create_client')
def test_get_user_found(mock_create_client):
    # Arrange
    mock_client, mock_table_customer, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    customer_data = [
        {
            'name': 'John Doe',
            'username': 'johndoe',
            'password': 'password123',
            'age': 30,
            'address': '123 Main St',
            'gender': True,
            'marital_status': 'single',
            'role': 'customer'
        }
    ]

    # Mock get_users method
    with patch.object(customer_table, 'get_users', return_value=customer_data) as mock_get_users:
        # Act
        result = customer_table.get_user('johndoe')

    # Assert
    assert result == [Customer.model_validate(customer_data[0])]
    mock_get_users.assert_called_once_with(username='johndoe')


@patch('app.models.create_client')
def test_get_user_not_found(mock_create_client):
    # Arrange
    mock_client, _, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    # Mock get_users method
    with patch.object(customer_table, 'get_users', return_value=[]) as mock_get_users:
        # Act
        result = customer_table.get_user('nonexistentuser')

    # Assert
    assert result == []
    mock_get_users.assert_called_once_with(username='nonexistentuser')


@patch('app.models.create_client')
def test_get_wallet_success(mock_create_client):
    # Arrange
    mock_client, _, mock_table_wallet = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    wallet_data = [
        {
            'customer_id': 'johndoe',
            'amount': 100.0,
            'last_updated': None
        }
    ]

    # Mock the select and filter methods
    mock_query = MagicMock()
    mock_table_wallet.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.execute.return_value.data = wallet_data

    # Act
    result = customer_table.get_wallet('johndoe')

    # Assert
    assert result == [Wallet.model_validate(wallet_data[0])]
    mock_table_wallet.select.assert_called_once_with('*')
    mock_query.eq.assert_called_once_with('customer_id', 'johndoe')
    mock_query.execute.assert_called_once()


@patch('app.models.create_client')
def test_get_wallet_not_found(mock_create_client):
    # Arrange
    mock_client, _, mock_table_wallet = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    # Mock the select and filter methods
    mock_query = MagicMock()
    mock_table_wallet.select.return_value = mock_query
    mock_query.eq.return_value = mock_query
    mock_query.execute.return_value.data = None

    # Act
    result = customer_table.get_wallet('nonexistentuser')

    # Assert
    assert result == []
    mock_table_wallet.select.assert_called_once_with('*')
    mock_query.eq.assert_called_once_with('customer_id', 'nonexistentuser')
    mock_query.execute.assert_called_once()


@patch('app.models.create_client')
def test_update_wallet_success(mock_create_client):
    # Arrange
    mock_client, _, mock_table_wallet = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    existing_wallet = [
        Wallet(
            customer_id='johndoe',
            amount=100.0,
            last_updated=None
        )
    ]

    updated_wallet_data = [
        {
            'customer_id': 'johndoe',
            'amount': 150.0,
            'last_updated': None
        }
    ]

    # Mock get_wallet method
    with patch.object(customer_table, 'get_wallet', return_value=existing_wallet) as mock_get_wallet:
        # Mock the update method
        mock_table_wallet.update.return_value.eq.return_value.execute.return_value.data = updated_wallet_data

        # Act
        result = customer_table.update_wallet('johndoe', 50.0)

    # Assert
    assert result == [Wallet.model_validate(updated_wallet_data[0])]
    mock_get_wallet.assert_called_once_with('johndoe')
    mock_table_wallet.update.assert_called_once_with({'amount': 150.0})
    mock_table_wallet.update.return_value.eq.assert_called_once_with('customer_id', 'johndoe')
    mock_table_wallet.update.return_value.eq.return_value.execute.assert_called_once()


@patch('app.models.create_client')
def test_update_wallet_wallet_not_found(mock_create_client):
    # Arrange
    mock_client, _, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    # Mock get_wallet method to return empty list
    with patch.object(customer_table, 'get_wallet', return_value=[]) as mock_get_wallet:
        # Act
        result = customer_table.update_wallet('nonexistentuser', 50.0)

    # Assert
    assert result == []
    mock_get_wallet.assert_called_once_with('nonexistentuser')


@patch('app.models.create_client')
def test_delete_user_success(mock_create_client):
    # Arrange
    mock_client, mock_table_customer, mock_table_wallet = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    # Mock get_users to return a user
    with patch.object(customer_table, 'get_users', return_value=[{'username': 'johndoe'}]) as mock_get_users:
        # Mock delete methods
        mock_table_customer.delete.return_value.eq.return_value.execute.return_value = None
        mock_table_wallet.delete.return_value.eq.return_value.execute.return_value = None

        # Act
        result = customer_table.delete_user('johndoe')

    # Assert
    assert result == True
    mock_get_users.assert_called_once_with(username='johndoe')
    mock_table_customer.delete.assert_called_once()
    mock_table_customer.delete.return_value.eq.assert_called_once_with('username', 'johndoe')
    mock_table_customer.delete.return_value.eq.return_value.execute.assert_called_once()
    mock_table_wallet.delete.assert_called_once()
    mock_table_wallet.delete.return_value.eq.assert_called_once_with('customer_id', 'johndoe')
    mock_table_wallet.delete.return_value.eq.return_value.execute.assert_called_once()


@patch('app.models.create_client')
def test_delete_user_not_found(mock_create_client):
    # Arrange
    mock_client, _, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    # Mock get_users to return None
    with patch.object(customer_table, 'get_users', return_value=None) as mock_get_users:
        # Act
        result = customer_table.delete_user('nonexistentuser')

    # Assert
    assert result == False
    mock_get_users.assert_called_once_with(username='nonexistentuser')


@patch('app.models.create_client')
def test_update_user_success(mock_create_client):
    # Arrange
    mock_client, mock_table_customer, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    existing_customer = {
        'name': 'John Doe',
        'username': 'johndoe',
        'password': 'password123',
        'age': 30,
        'address': '123 Main St',
        'gender': True,
        'marital_status': 'single',
        'role': 'customer'
    }

    updated_customer_data = [
        {
            'name': 'John Smith',
            'username': 'johndoe',
            'password': 'password123',
            'age': 31,
            'address': '123 Main St',
            'gender': True,
            'marital_status': 'married',
            'role': 'customer'
        }
    ]

    new_customer = Customer(
        name='John Smith',
        username='johndoe',
        password='password123',
        age=31,
        address='123 Main St',
        gender=True,
        marital_status='married',
        role='customer'
    )

    # Mock get_users to return existing customer
    with patch.object(customer_table, 'get_users', return_value=[existing_customer]) as mock_get_users:
        # Mock the update method
        mock_table_customer.update.return_value.eq.return_value.execute.return_value.data = updated_customer_data

        # Act
        result = customer_table.update_user('johndoe', new_customer)

    # Assert
    assert result == [Customer.model_validate(updated_customer_data[0])]
    mock_get_users.assert_called_once_with(username='johndoe')
    mock_table_customer.update.assert_called_once_with(new_customer.model_dump(exclude={'username'}))
    mock_table_customer.update.return_value.eq.assert_called_once_with('username', new_customer.username)
    mock_table_customer.update.return_value.eq.return_value.execute.assert_called_once()


@patch('app.models.create_client')
def test_update_user_not_found(mock_create_client):
    # Arrange
    mock_client, _, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    new_customer = Customer(
        name='Nonexistent User',
        username='nonexistentuser',
        password='password123',
        age=31,
        address='123 Main St',
        gender=True,
        marital_status='married',
        role='customer'
    )

    # Mock get_users to return None
    with patch.object(customer_table, 'get_users', return_value=None) as mock_get_users:
        # Act
        result = customer_table.update_user('nonexistentuser', new_customer)

    # Assert
    assert result == []
    mock_get_users.assert_called_once_with(username='nonexistentuser')


# Additional tests for deduct_wallet and charge_wallet can be similarly added

@patch('app.models.create_client')
def test_deduct_wallet_success(mock_create_client):
    # Arrange
    mock_client, _, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    with patch.object(customer_table, 'update_wallet') as mock_update_wallet:
        mock_update_wallet.return_value = 'Updated Wallet'

        # Act
        result = customer_table.deduct_wallet('johndoe', -50.0)

    # Assert
    assert result == 'Updated Wallet'
    mock_update_wallet.assert_called_once_with('johndoe', -50.0)


@patch('app.models.create_client')
def test_deduct_wallet_invalid_amount(mock_create_client):
    # Arrange
    mock_client, _, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    # Act & Assert
    with pytest.raises(AssertionError) as exc_info:
        customer_table.deduct_wallet('johndoe', 50.0)
    assert str(exc_info.value) == 'Amount must be less than 0'


@patch('app.models.create_client')
def test_charge_wallet_success(mock_create_client):
    # Arrange
    mock_client, _, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    with patch.object(customer_table, 'update_wallet') as mock_update_wallet:
        mock_update_wallet.return_value = 'Updated Wallet'

        # Act
        result = customer_table.charge_wallet('johndoe', 50.0)

    # Assert
    assert result == 'Updated Wallet'
    mock_update_wallet.assert_called_once_with('johndoe', 50.0)


@patch('app.models.create_client')
def test_charge_wallet_invalid_amount(mock_create_client):
    # Arrange
    mock_client, _, _ = create_mock_supabase_client()
    mock_create_client.return_value = mock_client

    customer_table = CustomerTable('http://example.com', 'fake_key')

    # Act & Assert
    with pytest.raises(AssertionError) as exc_info:
        customer_table.charge_wallet('johndoe', -50.0)
    assert str(exc_info.value) == 'Amount must be greater than or equal 0'

