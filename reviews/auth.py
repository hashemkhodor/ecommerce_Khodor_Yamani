from datetime import datetime, timedelta
from typing import Union, TypedDict
import jwt
from jwt import DecodeError, ExpiredSignatureError
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer

# Constants
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/reviews/auth/login")




class Customer(TypedDict):
    name: str
    username: str
    age: int
    address: str
    gender: bool
    marital_status: str
    role: str


def create_access_token(customer: Customer, expires_delta: timedelta = timedelta(hours=1)) -> str:
    """
    Create a JWT token for a Customer.

    Args:
        customer (Customer): The customer object for which to create the token.
        expires_delta (timedelta): The token expiry duration (default is 1 hour).

    Returns:
        str: A JWT token as a string.
    """
    # Prepare the payload, excluding sensitive data like the password
    to_encode = {
        "name": customer.get("name"),
        "username": customer.get("username"),
        "age": customer.get("age"),
        "address": customer.get("address"),
        "gender": customer.get("gender"),
        "marital_status": customer.get("marital_status"),
        "role": customer.get("role"),
        "exp": datetime.utcnow() + expires_delta,  # Expiry time
    }

    # Encode and return the JWT token
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> Union[dict, str]:
    """
    Decode and verify a JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Union[dict, str]: The payload as a dictionary if valid, or an error message if invalid.
    """
    try:
        # Decode the token and verify its signature and expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        return "Token has expired."
    except DecodeError:
        return "Invalid token."



def get_current_user(authorization: str = Header(None)) -> dict:
    """
    Decode and verify the current user from the JWT token in the Authorization header.

    Args:
        authorization (str): The Authorization header containing the Bearer token.

    Returns:
        dict: Decoded payload with user information.

    Raises:
        HTTPException: If the token is missing, invalid, or expired.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split("Bearer ")[1]  # Extract token

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
# Example usage
if __name__ == "__main__":
    # Generate a token for demonstration
    example_customer = Customer(
        name="John Doe",
        username="johndoe",
        password="securepassword",
        age=30,
        address="123 Main Street",
        gender=True,
        marital_status="single",
        role="customer"
    )

    # Create a JWT token
    token = create_access_token(example_customer)
    print("Generated Token:", token)

    # Decode the token
    decoded_payload = decode_access_token(token)
    print("Decoded Payload:", decoded_payload)
