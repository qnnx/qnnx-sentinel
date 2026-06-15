"""Current QNNX Sentinel schema baseline.

Revision ID: 0001_schema_baseline
Revises:
"""
from alembic import op

revision = "0001_schema_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE SCHEMA IF NOT EXISTS crypto")
    op.execute("CREATE SCHEMA IF NOT EXISTS analytics")
    op.execute("CREATE SCHEMA IF NOT EXISTS audit")
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.users (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid()
                REFERENCES auth.users(id) ON DELETE CASCADE,
            full_name text,
            role text NOT NULL DEFAULT 'user',
            organization_name text,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS crypto.algorithms (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            name text NOT NULL UNIQUE,
            type text NOT NULL,
            security_level text NOT NULL,
            nist_standard text NOT NULL,
            status text NOT NULL DEFAULT 'active',
            recommended_use text,
            description text,
            created_at timestamptz NOT NULL DEFAULT now(),
            algo_id text NOT NULL UNIQUE,
            algo_type text,
            family text,
            public_key_size text,
            private_key_size text,
            ciphertext_size text
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.api_keys (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
            name text NOT NULL,
            key_hash text NOT NULL UNIQUE,
            status text NOT NULL DEFAULT 'active',
            last_used_at timestamptz,
            created_at timestamptz NOT NULL DEFAULT now(),
            key_prefix text,
            signing_secret_hash text,
            revoked_at timestamptz
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.api_nonces (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            api_key_id uuid NOT NULL REFERENCES public.api_keys(id) ON DELETE CASCADE,
            nonce text NOT NULL,
            created_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (api_key_id, nonce)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS public.api_security_events (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid REFERENCES public.users(id) ON DELETE SET NULL,
            api_key_id uuid REFERENCES public.api_keys(id) ON DELETE SET NULL,
            event_type text NOT NULL,
            endpoint text,
            method text,
            ip_address text,
            user_agent text,
            details jsonb,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS crypto.keys (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
            algorithm_id uuid NOT NULL REFERENCES crypto.algorithms(id),
            key_type text NOT NULL,
            status text NOT NULL DEFAULT 'active',
            public_key text NOT NULL,
            private_key_ref text,
            expires_at timestamptz,
            created_at timestamptz NOT NULL DEFAULT now(),
            storage_mode text NOT NULL DEFAULT 'customer_managed',
            private_key_exported boolean NOT NULL DEFAULT false,
            name text,
            purpose text,
            key_strength text
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS analytics.api_usage (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid REFERENCES public.users(id) ON DELETE SET NULL,
            api_key_id uuid REFERENCES public.api_keys(id) ON DELETE SET NULL,
            endpoint text NOT NULL,
            method text NOT NULL,
            operation text NOT NULL,
            algorithm text,
            response_status integer NOT NULL,
            response_time_ms integer,
            success boolean NOT NULL,
            ip_address text,
            user_agent text,
            error_type text,
            created_at timestamptz NOT NULL DEFAULT now()
        )
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS audit.audit_logs (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid REFERENCES public.users(id),
            event_type text NOT NULL,
            resource_type text,
            resource_id text,
            status text NOT NULL,
            ip_address text,
            details jsonb,
            created_at timestamptz NOT NULL DEFAULT now(),
            api_key_id uuid REFERENCES public.api_keys(id) ON DELETE SET NULL
        )
        """
    )
    for statement in (
        "CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON public.api_keys (user_id)",
        "CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON public.api_keys (key_hash)",
        "CREATE INDEX IF NOT EXISTS idx_api_nonces_api_key_id ON public.api_nonces (api_key_id)",
        "CREATE INDEX IF NOT EXISTS idx_api_nonces_created_at ON public.api_nonces (created_at)",
        "CREATE INDEX IF NOT EXISTS idx_api_security_events_user_id ON public.api_security_events (user_id)",
        "CREATE INDEX IF NOT EXISTS idx_api_security_events_api_key_id ON public.api_security_events (api_key_id)",
        "CREATE INDEX IF NOT EXISTS idx_api_security_events_event_type ON public.api_security_events (event_type)",
        "CREATE INDEX IF NOT EXISTS idx_api_security_events_created_at ON public.api_security_events (created_at)",
        "CREATE INDEX IF NOT EXISTS idx_keys_user_id ON crypto.keys (user_id)",
        "CREATE INDEX IF NOT EXISTS idx_keys_algorithm_id ON crypto.keys (algorithm_id)",
        "CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON analytics.api_usage (user_id)",
        "CREATE INDEX IF NOT EXISTS idx_api_usage_api_key_id ON analytics.api_usage (api_key_id)",
        "CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON analytics.api_usage (created_at)",
        "CREATE INDEX IF NOT EXISTS idx_api_usage_operation ON analytics.api_usage (operation)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit.audit_logs (user_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_api_key_id ON audit.audit_logs (api_key_id)",
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit.audit_logs (created_at)",
    ):
        op.execute(statement)


def downgrade() -> None:
    # Never drop an existing production schema from a baseline downgrade.
    pass
