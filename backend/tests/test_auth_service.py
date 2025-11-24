import pytest
from services.auth_service import create_access_token
from datetime import timedelta

@pytest.mark.skip(reason="bcrypt compatibility issue with Python 3.13")
def test_password_hashing():
    """Test password hashing and verification"""
    from services.auth_service import verify_password, get_password_hash
    password = "test_pass_123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_pass", hashed)

def test_create_access_token():
    """Test JWT token creation"""
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_create_access_token_with_expiry():
    """Test JWT token with custom expiry"""
    data = {"sub": "test@example.com"}
    expires = timedelta(minutes=30)
    token = create_access_token(data, expires_delta=expires)
    
    assert token is not None
    assert isinstance(token, str)