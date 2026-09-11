from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings


# ============================================================
# PASSWORD CONFIGURATION
# ============================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


# ============================================================
# PASSWORD HASHING
# ============================================================

def hash_password(password: str) -> str:
    """
    Hash a user's password using bcrypt.
    """

    if not password:
        raise ValueError("Password cannot be empty")

    # bcrypt supports a maximum of 72 bytes.
    # We explicitly validate instead of silently truncating.
    if len(password.encode("utf-8")) > 72:
        raise ValueError(
            "Password cannot be longer than 72 bytes"
        )

    return pwd_context.hash(password)


# ============================================================
# PASSWORD VERIFICATION
# ============================================================

def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    """
    Verify a plain password against its stored hash.
    """

    if not plain_password or not hashed_password:
        return False

    if len(plain_password.encode("utf-8")) > 72:
        return False

    return pwd_context.verify(
        plain_password,
        hashed_password,
    )


# ============================================================
# CREATE JWT ACCESS TOKEN
# ============================================================

def create_access_token(subject: str) -> str:
    """
    Create a JWT access token for the authenticated user.
    """

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(subject),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


# ============================================================
# DECODE JWT ACCESS TOKEN
# ============================================================

def decode_access_token(token: str) -> dict:
    """
    Decode and validate a JWT access token.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        return payload

    except JWTError:
        return {}