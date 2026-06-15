"""Reference application users from user-owned records.

Revision ID: 0003_reference_public_users
Revises: 0002_runtime_alignment_and_rls
"""
from alembic import op

revision = "0003_reference_public_users"
down_revision = "0002_runtime_alignment_and_rls"
branch_labels = None
depends_on = None


USER_FOREIGN_KEYS = (
    (
        "public.api_security_events",
        "api_security_events_user_id_fkey",
        "SET NULL",
    ),
    (
        "crypto.keys",
        "keys_user_id_fkey",
        "CASCADE",
    ),
    (
        "analytics.api_usage",
        "api_usage_user_id_fkey",
        "SET NULL",
    ),
    (
        "audit.audit_logs",
        "audit_logs_user_id_fkey",
        None,
    ),
)


def _replace_user_foreign_keys(referenced_table: str) -> None:
    for table, constraint, on_delete in USER_FOREIGN_KEYS:
        op.execute(
            f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint}"
        )
        delete_clause = f" ON DELETE {on_delete}" if on_delete else ""
        op.execute(
            f"ALTER TABLE {table} "
            f"ADD CONSTRAINT {constraint} "
            f"FOREIGN KEY (user_id) REFERENCES {referenced_table}(id)"
            f"{delete_clause}"
        )


def _backfill_public_users() -> None:
    op.execute(
        """
        INSERT INTO public.users (id)
        SELECT referenced_users.user_id
        FROM (
            SELECT user_id FROM public.api_security_events
            UNION
            SELECT user_id FROM crypto.keys
            UNION
            SELECT user_id FROM analytics.api_usage
            UNION
            SELECT user_id FROM audit.audit_logs
        ) AS referenced_users
        JOIN auth.users AS auth_user
          ON auth_user.id = referenced_users.user_id
        WHERE referenced_users.user_id IS NOT NULL
        ON CONFLICT (id) DO NOTHING
        """
    )


def upgrade() -> None:
    _backfill_public_users()
    _replace_user_foreign_keys("public.users")


def downgrade() -> None:
    _replace_user_foreign_keys("auth.users")
