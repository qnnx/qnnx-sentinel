"""Store encrypted API key signing secrets.

Revision ID: 0004_encrypted_api_key_signing_secret
Revises: 0003_reference_public_users
"""
from alembic import op

revision = "0004_encrypted_api_key_signing_secret"
down_revision = "0003_reference_public_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE public.api_keys "
        "ADD COLUMN IF NOT EXISTS signing_secret_encrypted text"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE public.api_keys "
        "DROP COLUMN IF EXISTS signing_secret_encrypted"
    )
