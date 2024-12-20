from datetime import datetime, timedelta
from typing import TypedDict, Union

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import DecodeError, ExpiredSignatureError

# Constants
SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"

# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/reviews/auth/login")


class Customer(TypedDict):
    """
    Represents a customer in the system.

    :param name: Full name of the customer.
    :type name: str
    :param username: Unique username of the customer.
    :type username: str
    :param age: Age of the customer.
    :type age: int
    :param address: Address of the customer.
    :type address: str
    :param gender: Gender of the customer (True for male, False for female).
    :type gender: bool
    :param marital_status: Marital status of the customer (e.g., single, married).
    :type marital_status: str
    :param role: Role of the customer (e.g., customer, admin).
    :type role: str
    """

    name: str
    username: str
    age: int
    address: str
    gender: bool
    marital_status: str
    role: str


def create_access_token(
    customer: Customer, expires_delta: timedelta = timedelta(hours=1)
) -> str:
    """
    Create a JWT token for a Customer.

    :param customer: The customer object for which to create the token.
    :type customer: Customer
    :param expires_delta: The token expiry duration (default is 1 hour).
    :type expires_delta: timedelta
    :return: A JWT token as a string.
    :rtype: str
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

    :param token: The JWT token to decode.
    :type token: str
    :return: The payload as a dictionary if valid, or an error message if invalid.
    :rtype: Union[dict, str]
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

    :param authorization: The Authorization header containing the Bearer token.
    :type authorization: str
    :return: Decoded payload with user information.
    :rtype: dict
    :raises HTTPException: If the token is missing, invalid, or expired.
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
        role="customer",
    )

    # Create a JWT token
    token = create_access_token(example_customer)
    print("Generated Token:", token)

    # Decode the token
    decoded_payload = decode_access_token(token)
    print("Decoded Payload:", decoded_payload)
