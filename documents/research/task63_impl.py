"""
Task 6.3: "Write an Authentication System"

Initial underspecified request. Scope to: user registration, login, token auth.
"""

from typing import Optional, Dict
from dataclasses import dataclass
from enum import Enum
from threading import Lock
import time
import uuid
import hashlib
import base64
import json


class UserRole(Enum):
    USER = "user"
    ADMIN = "admin"


@dataclass
class User:
    id: str
    username: str
    email: str
    hashed_password: str
    role: UserRole = UserRole.USER
    created_at: float = 0.0


class AuthException(Exception):
    pass


class InvalidCredentialsError(AuthException):
    pass


class AuthToken:
    """Simple token-based authentication."""
    
    def __init__(self, key: str = "default-key"):
        self._secret_key = key
    
    def generate_token(self, user_id: str, expires_in: int = 3600) -> str:
        """Generate authentication token."""
        payload = {
            "sub": user_id,
            "iat": time.time(),
            "exp": time.time() + expires_in
        }
        payload_str = json.dumps(payload)
        signature = hashlib.sha256((payload_str + self._secret_key).encode()).hexdigest()
        encoded_payload = base64.b64encode(payload_str.encode()).decode()
        return f"{encoded_payload}.{signature}"
    
    def validate_token(self, token: str) -> Optional[Dict]:
        """Validate token and return payload."""
        try:
            parts = token.split(".")
            if len(parts) != 2:
                return None
            
            # Decode payload first
            payload = json.loads(base64.b64decode(parts[0]).decode())
            
            # Verify signature against decoded payload
            payload_str = json.dumps(payload)
            expected_sig = hashlib.sha256((payload_str + self._secret_key).encode()).hexdigest()
            if parts[1] != expected_sig:
                return None
            
            # Check expiry
            if time.time() > payload["exp"]:
                return None
            
            return payload
        except Exception:
            return None


class AuthenticationService:
    """
    Simple authentication service.
    """
    
    def __init__(self, secret_key: str = "development-key"):
        self._users: Dict[str, User] = {}
        self._token_generator = AuthToken(secret_key)
        self._lock = Lock()
    
    def register(self, username: str, email: str, password: str) -> User:
        """Register a new user."""
        with self._lock:
            if username in self._users:
                raise AuthException("Username already exists")
            
            user = User(
                id=str(uuid.uuid4()),
                username=username,
                email=email,
                hashed_password=self._hash_password(password),
                created_at=time.time()
            )
            self._users[username] = user
            self._users[user.id] = user
            return user
    
    def login(self, username: str, password: str) -> Dict[str, str]:
        """Login and return auth token."""
        with self._lock:
            user = self._users.get(username)
            if not user or not self._verify_password(user.hashed_password, password):
                raise InvalidCredentialsError("Invalid credentials")
            
            token = self._token_generator.generate_token(user.id)
            return {"access_token": token}
    
    def get_user(self, token: str) -> Optional[User]:
        """Get user by authentication token."""
        payload = self._token_generator.validate_token(token)
        if not payload:
            return None
        return self._users.get(payload["sub"])
    
    def has_role(self, user: User, required_role: UserRole) -> bool:
        """Check if user has required role."""
        return user.role == required_role
    
    @staticmethod
    def _hash_password(password: str) -> str:
        """Hash a password."""
        salt = str(uuid.uuid4())
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${hashed}"
    
    @staticmethod
    def _verify_password(hashed_password: str, password: str) -> bool:
        """Verify a password against hash."""
        salt, hash_value = hashed_password.split("$")
        return hash_value == hashlib.sha256((password + salt).encode()).hexdigest()


def test_auth_system():
    """Test authentication system."""
    service = AuthenticationService()
    
    # Register
    user = service.register(
        "alice",
        "alice@example.com",
        "secure123"
    )
    assert user.id is not None
    
    # Login
    token_data = service.login("alice", "secure123")
    assert "access_token" in token_data
    
    # Get user from token
    retrieved_user = service.get_user(token_data["access_token"])
    assert retrieved_user.username == "alice"
    
    # Invalid credentials
    try:
        service.login("alice", "wrong")
        assert False
    except InvalidCredentialsError:
        pass
    
    print("Tests passed")


if __name__ == "__main__":
    test_auth_system()
