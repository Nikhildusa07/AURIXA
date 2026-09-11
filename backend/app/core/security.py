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

    try:
        return pwd_context.verify(
            plain_password,
            hashed_password,
        )

    except Exception:
        return False


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

def decode_access_token(token: str) -> str | None:
    """
    Decode and validate a JWT access token.

    Returns the user ID stored in the JWT subject.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("sub")

        if not user_id:
            return None

        return str(user_id)

    except JWTError:
        return None