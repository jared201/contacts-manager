from typing import List, Optional, Dict
from uuid import UUID
from datetime import datetime
import hashlib
import secrets

from models.user import User, UserCreate, UserUpdate, UserInDB

# In-memory storage for users
users_db: Dict[UUID, UserInDB] = {}


def get_users() -> List[User]:
    """
    Get all users (without password hashes).
    """
    return [User(**{k: v for k, v in user.__dict__.items() if k != 'hashed_password'}) 
            for user in users_db.values()]


def get_user(user_id: UUID) -> Optional[User]:
    """
    Get a user by ID (without password hash).
    """
    user = users_db.get(user_id)
    if user:
        return User(**{k: v for k, v in user.__dict__.items() if k != 'hashed_password'})
    return None


def get_user_by_username(username: str) -> Optional[User]:
    """
    Get a user by username (without password hash).
    """
    for user in users_db.values():
        if user.username == username:
            return User(**{k: v for k, v in user.__dict__.items() if k != 'hashed_password'})
    return None


def get_user_by_email(email: str) -> Optional[User]:
    """
    Get a user by email (without password hash).
    """
    for user in users_db.values():
        if user.email == email:
            return User(**{k: v for k, v in user.__dict__.items() if k != 'hashed_password'})
    return None


def create_user(user: UserCreate) -> User:
    """
    Create a new user.
    """
    # Check if username or email already exists
    if get_user_by_username(user.username):
        raise ValueError("Username already exists")
    if get_user_by_email(user.email):
        raise ValueError("Email already exists")
    
    # Hash the password
    hashed_password = _hash_password(user.password)
    
    # Handle both Pydantic v1 and v2
    user_data = user.model_dump() if hasattr(user, 'model_dump') else user.dict()
    
    # Remove the plain password
    user_data.pop('password')
    
    # Create the user with hashed password
    new_user = UserInDB(**user_data, hashed_password=hashed_password)
    users_db[new_user.id] = new_user
    
    # Return the user without the hashed password
    return User(**{k: v for k, v in new_user.__dict__.items() if k != 'hashed_password'})


def update_user(user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    """
    Update an existing user.
    """
    if user_id not in users_db:
        return None

    # Get the existing user
    user = users_db[user_id]

    # Handle both Pydantic v1 and v2
    if hasattr(user_update, 'model_dump'):
        update_data = user_update.model_dump(exclude_unset=True)
    else:
        update_data = user_update.dict(exclude_unset=True)

    # If updating username or email, check if they already exist
    if 'username' in update_data and update_data['username'] != user.username:
        if get_user_by_username(update_data['username']):
            raise ValueError("Username already exists")
    
    if 'email' in update_data and update_data['email'] != user.email:
        if get_user_by_email(update_data['email']):
            raise ValueError("Email already exists")
    
    # If updating password, hash it
    if 'password' in update_data:
        hashed_password = _hash_password(update_data.pop('password'))
        user.hashed_password = hashed_password

    # Update other fields
    for field, value in update_data.items():
        setattr(user, field, value)

    # Save the updated user
    users_db[user_id] = user
    
    # Return the user without the hashed password
    return User(**{k: v for k, v in user.__dict__.items() if k != 'hashed_password'})


def delete_user(user_id: UUID) -> bool:
    """
    Delete a user.
    """
    if user_id not in users_db:
        return False

    del users_db[user_id]
    return True


def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username and password.
    """
    for user in users_db.values():
        if user.username == username and _verify_password(password, user.hashed_password):
            # Update last login time
            user.last_login = datetime.now()
            users_db[user.id] = user
            return User(**{k: v for k, v in user.__dict__.items() if k != 'hashed_password'})
    return None


def _hash_password(password: str) -> str:
    """
    Hash a password for storing.
    """
    # In a real application, use a proper password hashing library like bcrypt or Argon2
    salt = secrets.token_hex(16)
    return hashlib.sha256(f"{password}{salt}".encode()).hexdigest() + ":" + salt


def _verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a stored password against a provided password.
    """
    # In a real application, use a proper password hashing library like bcrypt or Argon2
    stored_hash, salt = hashed_password.split(":")
    return hashlib.sha256(f"{plain_password}{salt}".encode()).hexdigest() == stored_hash