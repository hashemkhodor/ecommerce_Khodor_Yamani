from datetime import timedelta
import datetime
import jwt
from jwt import DecodeError, ExpiredSignatureError

from customer.schemas import Customer

SECRET_KEY = "your_secret_key_here"
ALGORITHM = "HS256"


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
        "name": customer.name,
        "username": customer.username,
        "age": customer.age,
        "address": customer.address,
        "gender": customer.gender,
        "marital_status": customer.marital_status,
        "role": customer.role,
        "exp": datetime.datetime.utcnow() + expires_delta,
    }

    # Encode and return the JWT token
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token


# Example Usage
def decode_access_token(token: str) -> dict | str:
    """
    Decode and verify a JWT token.

    Args:
        token (str): The JWT token to decode.

    Returns:
        Union[dict, str]: Returns the payload as a dictionary if valid, or an error message if invalid.
    """
    try:
        # Decode the token and verify its signature and expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        return "Token has expired."
    except DecodeError:
        return "Invalid token."


from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

# Define the OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Dependency to verify the JWT token
def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Return the token payload (user information)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.DecodeError:
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
    token = create_access_token(example_customer)
    print("Generated Token:", token)

    # Decode the token
    decoded_payload = decode_access_token(token)
    print("Decoded Payload:", decoded_payload)
