"""Align executable algorithms and restrict sensitive read policies.

Revision ID: 0002_runtime_alignment_and_rls
Revises: 0001_schema_baseline
"""
from alembic import op

revision = "0002_runtime_alignment_and_rls"
down_revision = "0001_schema_baseline"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        WITH ranked AS (
            SELECT id, row_number() OVER (
                PARTITION BY key_hash ORDER BY created_at, id
            ) AS position
            FROM public.api_keys
        )
        UPDATE public.api_keys AS api_key
        SET key_hash = encode(
                digest(api_key.key_hash || api_key.id::text, 'sha256'),
                'hex'
            ),
            status = 'revoked',
            revoked_at = COALESCE(api_key.revoked_at, now())
        FROM ranked
        WHERE api_key.id = ranked.id
          AND ranked.position > 1
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'api_keys_key_hash_key'
                  AND conrelid = 'public.api_keys'::regclass
            ) THEN
                ALTER TABLE public.api_keys
                ADD CONSTRAINT api_keys_key_hash_key UNIQUE (key_hash);
            END IF;
        END $$;
        """
    )
    op.execute("CREATE INDEX IF NOT EXISTS idx_keys_user_id ON crypto.keys (user_id)")
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_keys_algorithm_id "
        "ON crypto.keys (algorithm_id)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS idx_audit_logs_api_key_id "
        "ON audit.audit_logs (api_key_id)"
    )
    op.execute(
        """
        UPDATE crypto.algorithms
        SET name = 'ML-DSA-87', algo_id = 'ml-dsa-87'
        WHERE algo_id = 'ml-dsa-85'
        """
    )
    op.execute(
        """
        UPDATE crypto.algorithms
        SET status = 'disabled'
        WHERE algo_id = 'sphincs-plus'
        """
    )
    op.execute(
        'DROP POLICY IF EXISTS "Allow public read access for analytics logs" '
        "ON analytics.api_usage"
    )
    op.execute(
        'DROP POLICY IF EXISTS "Allow read access for everyone" '
        "ON public.api_security_events"
    )
    op.execute(
        'DROP POLICY IF EXISTS "Service role can manage API usage" '
        "ON analytics.api_usage"
    )
    op.execute(
        'CREATE POLICY "Service role can manage API usage" '
        "ON analytics.api_usage FOR ALL TO service_role "
        "USING (true) WITH CHECK (true)"
    )
    op.execute(
        'DROP POLICY IF EXISTS "Users can view own security events" '
        "ON public.api_security_events"
    )
    op.execute(
        'CREATE POLICY "Users can view own security events" '
        "ON public.api_security_events FOR SELECT TO authenticated "
        "USING (auth.uid() = user_id)"
    )
    op.execute(
        'DROP POLICY IF EXISTS "Service role can manage security events" '
        "ON public.api_security_events"
    )
    op.execute(
        'CREATE POLICY "Service role can manage security events" '
        "ON public.api_security_events FOR ALL TO service_role "
        "USING (true) WITH CHECK (true)"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE public.api_keys "
        "DROP CONSTRAINT IF EXISTS api_keys_key_hash_key"
    )
    op.execute("DROP INDEX IF EXISTS crypto.idx_keys_user_id")
    op.execute("DROP INDEX IF EXISTS crypto.idx_keys_algorithm_id")
    op.execute("DROP INDEX IF EXISTS audit.idx_audit_logs_api_key_id")
    op.execute(
        """
        UPDATE crypto.algorithms
        SET name = 'ML-DSA-85', algo_id = 'ml-dsa-85'
        WHERE algo_id = 'ml-dsa-87'
        """
    )
    op.execute(
        "UPDATE crypto.algorithms SET status = 'active' "
        "WHERE algo_id = 'sphincs-plus'"
    )
    op.execute(
        'DROP POLICY IF EXISTS "Service role can manage API usage" '
        "ON analytics.api_usage"
    )
    op.execute(
        'CREATE POLICY "Allow public read access for analytics logs" '
        "ON analytics.api_usage FOR SELECT TO anon USING (true)"
    )
    op.execute(
        'DROP POLICY IF EXISTS "Users can view own security events" '
        "ON public.api_security_events"
    )
    op.execute(
        'DROP POLICY IF EXISTS "Service role can manage security events" '
        "ON public.api_security_events"
    )
    op.execute(
        'CREATE POLICY "Allow read access for everyone" '
        "ON public.api_security_events FOR SELECT TO anon, authenticated USING (true)"
    )
