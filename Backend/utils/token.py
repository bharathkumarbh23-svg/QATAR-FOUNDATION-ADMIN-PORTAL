import secrets
import logging
from datetime import datetime, timedelta

from extensions import db
from models import PasswordResetToken

logger = logging.getLogger(__name__)

TOKEN_EXPIRY_HOURS = 1


def generate_reset_token(admin) -> str:
    """
    Invalidate any existing unused tokens for the admin,
    create a new one, persist it, and return the raw token string.
    """
    # Invalidate old tokens
    PasswordResetToken.query.filter_by(
        admin_id=admin.id, used=False
    ).update({'used': True})
    db.session.commit()

    raw_token  = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRY_HOURS)

    record = PasswordResetToken(
        admin_id=admin.id,
        token=raw_token,
        expires_at=expires_at,
    )
    db.session.add(record)
    db.session.commit()

    return raw_token


def build_reset_link(token: str, base_url: str = 'http://localhost:5000') -> str:
    return f'{base_url}/reset-password?token={token}'


def log_reset_link(email: str, token: str, base_url: str = 'http://localhost:5000') -> None:
    """Log the reset link internally (no email sending needed at this stage)."""
    link = build_reset_link(token, base_url)
    logger.info(
        '[PASSWORD RESET] email=%s | link=%s | expires_in=%dh',
        email, link, TOKEN_EXPIRY_HOURS
    )


def consume_reset_token(raw_token: str) -> tuple[PasswordResetToken | None, str | None]:
    """
    Look up and validate a raw token.
    Returns (record, None) on success or (None, error_message) on failure.
    """
    record = PasswordResetToken.query.filter_by(token=raw_token, used=False).first()

    if not record:
        return None, 'Invalid or expired reset link.'

    if datetime.utcnow() > record.expires_at:
        record.used = True
        db.session.commit()
        return None, 'This reset link has expired. Please request a new one.'

    return record, None
