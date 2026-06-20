import base64
import logging
import uuid
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict
from psycopg2 import pool

from app.core.config import settings

logger = logging.getLogger(__name__)


class KeyVaultError(Exception):
    """Base exception for all PQC Key Vault errors."""
    pass


def _wipe_bytearray(ba: bytearray | None) -> None:
    """
    Best-effort memory scrubbing by zeroing out the bytearray buffer.
    Helps minimize the time private key bytes remain in plaintext memory.
    """
    if ba is not None:
        try:
            for i in range(len(ba)):
                ba[i] = 0
        except Exception:
            pass


class PQCKeyVault:
    """
    Manages post-quantum cryptography (PQC) keys using Supabase Vault
    for secure private key storage and the local crypto.keys table for metadata.
    """

    def __init__(self, connection_pool: pool.AbstractConnectionPool | None = None):
        """
        Initializes the PQCKeyVault. Uses the provided connection pool or creates a
        new ThreadedConnectionPool using the configured DATABASE_URL.
        """
        if connection_pool is None:
            try:
                self.pool = pool.ThreadedConnectionPool(
                    minconn=1,
                    maxconn=10,
                    dsn=settings.DATABASE_URL
                )
                self._owned_pool = True
            except Exception as e:
                logger.error("Failed to initialize database connection pool: %s", e)
                raise KeyVaultError("Database connection pool initialization failed") from e
        else:
            self.pool = connection_pool
            self._owned_pool = False

    @contextmanager
    def _get_connection(self):
        """Context manager to lease and return connections from the pool."""
        conn = self.pool.getconn()
        try:
            conn.autocommit = True
            yield conn
        finally:
            self.pool.putconn(conn)

    def close(self) -> None:
        """Closes the connection pool if it was initialized and owned by this instance."""
        if self._owned_pool and hasattr(self, "pool"):
            try:
                self.pool.closeall()
            except Exception as e:
                logger.warning("Error closing connection pool: %s", e)

    def generate_keypair(self, owner_id: uuid.UUID, algorithm: str) -> Dict[str, Any]:
        """
        Generates a post-quantum cryptographic keypair (KEM or DSA).
        Stores the private key in Supabase Vault and the metadata in the crypto.keys table.

        CRITICAL SECURITY CONTRACT:
        This method must NEVER return the raw private key, expose it in logs, or print
        it. Private key bytes must go out of scope immediately after being passed to the Vault
        and are cleared from memory.
        """
        # NOTE: Do NOT add the private key to the return dict, log statements,
        # exception messages, or caches (even temporarily for debugging).
        
        # Resolve algorithm details
        from app.services.key_service import _resolve_algorithm
        try:
            key_type, canonical_algorithm = _resolve_algorithm(algorithm)
        except Exception as e:
            logger.error("Algorithm resolution failed for %s: %s", algorithm, e)
            raise KeyVaultError(f"Unsupported or disabled algorithm: {algorithm}") from e

        # Resolve algorithm ID from database
        algorithm_id = self._get_algorithm_id(canonical_algorithm)
        if not algorithm_id:
            raise KeyVaultError(f"Algorithm ID not found in database for name: {canonical_algorithm}")

        # Import cryptographic services locally to generate keypair
        from app.services import dsa_service, kem_service

        raw_priv_key_bytes = None
        vault_secret_id = None
        key_id = uuid.uuid4()

        try:
            if key_type == "kem":
                raw_response = kem_service.generate_kem_keypair(canonical_algorithm)
            else:
                raw_response = dsa_service.generate_dsa_keypair(canonical_algorithm)

            raw_pub_key_bytes = raw_response["public_key"]
            raw_priv_key_bytes = bytearray(raw_response["private_key"])  # Wrap in mutable bytearray immediately

            # Base64-encode public key for metadata storage
            public_key_b64 = base64.b64encode(raw_pub_key_bytes).decode("ascii")

            # 1. Store private key in Vault first
            vault_secret_id = self._create_vault_secret(
                secret_bytes=raw_priv_key_bytes,
                name=f"pqc-key-{key_id}",
                description=f"Sentinel-managed private key for key_id {key_id}"
            )

            # 2. Insert into crypto.keys
            self._insert_key_metadata(
                key_id=key_id,
                owner_id=owner_id,
                algorithm_id=algorithm_id,
                key_type=key_type,
                public_key_b64=public_key_b64,
                private_key_ref=vault_secret_id
            )

            # Fetch the generated creation time
            created_at = self._get_key_creation_time(key_id)

            return {
                "key_id": str(key_id),
                "public_key": public_key_b64,
                "algorithm": canonical_algorithm,
                "created_at": created_at.isoformat() if created_at else datetime.utcnow().isoformat()
            }

        except Exception as e:
            # Coordinated Rollback: Delete Vault secret if DB update failed to prevent orphan secrets
            if vault_secret_id:
                try:
                    logger.warning("DB insert failed; deleting vault secret %s to prevent orphans", vault_secret_id)
                    self._delete_vault_secret(vault_secret_id)
                except Exception as rollback_err:
                    logger.critical("CRITICAL rollback failure: Failed to delete orphaned Vault secret %s: %s", vault_secret_id, rollback_err)
            
            logger.error("Failed to generate and store PQC keypair: %s", str(e))
            raise KeyVaultError("Key generation and vault storage failed") from e

        finally:
            # Memory Scrubbing
            _wipe_bytearray(raw_priv_key_bytes)

    def store_private_key(self, key_id: uuid.UUID, key_bytes: bytes, algorithm: str) -> str:
        """
        Internal method to store an existing raw private key in Vault
        and link it to the crypto.keys record. Wipes raw key material from memory.
        """
        secret_bytes = bytearray(key_bytes)
        vault_secret_id = None
        try:
            vault_secret_id = self._create_vault_secret(
                secret_bytes=secret_bytes,
                name=f"pqc-key-{key_id}",
                description=f"Sentinel-managed private key for key_id {key_id}"
            )

            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE crypto.keys SET private_key_ref = %s WHERE id = %s;",
                        (vault_secret_id, str(key_id))
                    )
                    if cur.rowcount == 0:
                        raise KeyVaultError(f"No key metadata record found for key_id {key_id}")
            return vault_secret_id
        except Exception as e:
            if vault_secret_id:
                try:
                    self._delete_vault_secret(vault_secret_id)
                except Exception as rollback_err:
                    logger.critical("CRITICAL: Storing secret rollback failed for ref %s: %s", vault_secret_id, rollback_err)
            raise KeyVaultError("Failed to store private key") from e
        finally:
            _wipe_bytearray(secret_bytes)

    def get_private_key(self, key_id: uuid.UUID) -> bytes:
        """
        Retrieves and decrypts the private key bytes from Supabase Vault.

        WARNING: This method returns raw decrypted private key bytes in memory.
        It must ONLY be called internally by signing or decapsulation engines
        and NEVER returned via endpoints, logs, or stored in persistent caches.
        """
        try:
            # 1. Get private_key_ref from keys table
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT private_key_ref FROM crypto.keys WHERE id = %s;",
                        (str(key_id),)
                    )
                    row = cur.fetchone()
                    if not row:
                        raise KeyVaultError(f"Key record {key_id} not found in database")
                    private_key_ref = row[0]
                    if not private_key_ref:
                        raise KeyVaultError(f"Key record {key_id} has no private key reference (may be revoked/deleted)")

            # 2. Retrieve the decrypted secret
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT decrypted_secret FROM vault.decrypted_secrets WHERE id = %s::uuid;",
                        (private_key_ref,)
                    )
                    row = cur.fetchone()
                    if not row or not row[0]:
                        raise KeyVaultError(f"Decrypted secret not found in Vault for reference: {private_key_ref}")
                    decrypted_b64 = row[0]

            # 3. Decode base64
            return base64.b64decode(decrypted_b64)
        except Exception as e:
            logger.error("Failed to retrieve private key for key_id %s (material hidden)", key_id)
            raise KeyVaultError("Failed to retrieve private key from Vault") from e

    def rotate_key(self, key_id: uuid.UUID, new_key_bytes: bytes) -> None:
        """
        Rotates the private key by updating the existing secret in Supabase Vault.
        No database update is needed on crypto.keys as the reference UUID remains the same.
        """
        secret_bytes = bytearray(new_key_bytes)
        try:
            # 1. Get private_key_ref from keys table
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT private_key_ref FROM crypto.keys WHERE id = %s;",
                        (str(key_id),)
                    )
                    row = cur.fetchone()
                    if not row:
                        raise KeyVaultError(f"Key record {key_id} not found in database")
                    private_key_ref = row[0]
                    if not private_key_ref:
                        raise KeyVaultError(f"Key record {key_id} has no private key reference to rotate")

            # 2. Update vault secret
            secret_b64 = base64.b64encode(secret_bytes).decode("ascii")
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT vault.update_secret(%s::uuid, %s);",
                        (private_key_ref, secret_b64)
                    )
        except Exception as e:
            logger.error("Failed to rotate private key for key_id %s", key_id)
            raise KeyVaultError("Key rotation failed") from e
        finally:
            _wipe_bytearray(secret_bytes)

    def delete_key(self, key_id: uuid.UUID) -> None:
        """
        Deletes the private key secret from Supabase Vault, nulls out the
        private_key_ref reference in the database, and marks the status as 'revoked'.
        This retains key metadata for verifying historical signatures while destroying the secret.
        """
        try:
            # 1. Retrieve the private_key_ref
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT private_key_ref FROM crypto.keys WHERE id = %s;",
                        (str(key_id),)
                    )
                    row = cur.fetchone()
                    if not row:
                        raise KeyVaultError(f"Key record {key_id} not found in database")
                    private_key_ref = row[0]

            # 2. Delete the secret from vault if it exists
            if private_key_ref:
                with self._get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "DELETE FROM vault.secrets WHERE id = %s::uuid;",
                            (private_key_ref,)
                        )

            # 3. Update the key status and null reference
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "UPDATE crypto.keys SET private_key_ref = NULL, status = 'revoked' WHERE id = %s;",
                        (str(key_id),)
                    )
        except Exception as e:
            logger.error("Failed to delete private key for key_id %s", key_id)
            raise KeyVaultError("Key deletion failed") from e

    # --- Internal SQL Helpers ---

    def _create_vault_secret(self, secret_bytes: bytearray, name: str, description: str) -> str:
        secret_b64 = base64.b64encode(secret_bytes).decode("ascii")
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT vault.create_secret(%s, %s, %s);",
                        (secret_b64, name, description)
                    )
                    row = cur.fetchone()
                    if not row or not row[0]:
                        raise KeyVaultError("Vault creation returned an empty ID")
                    return str(row[0])
        except Exception as e:
            logger.error("Failed to insert secret to Vault: %s", str(e))
            raise KeyVaultError("Vault write failed") from e

    def _delete_vault_secret(self, secret_id: str) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM vault.secrets WHERE id = %s::uuid;",
                    (secret_id,)
                )

    def _insert_key_metadata(
        self,
        key_id: uuid.UUID,
        owner_id: uuid.UUID,
        algorithm_id: uuid.UUID,
        key_type: str,
        public_key_b64: str,
        private_key_ref: str
    ) -> None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO crypto.keys (id, user_id, algorithm_id, key_type, public_key, private_key_ref, status, storage_mode, private_key_exported)
                    VALUES (%s, %s, %s, %s, %s, %s, 'active', 'sentinel_managed', false);
                    """,
                    (str(key_id), str(owner_id), str(algorithm_id), key_type, public_key_b64, private_key_ref)
                )

    def _get_algorithm_id(self, canonical_name: str) -> uuid.UUID | None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT id FROM crypto.algorithms WHERE name = %s;",
                    (canonical_name,)
                )
                row = cur.fetchone()
                return uuid.UUID(row[0]) if row else None

    def _get_key_creation_time(self, key_id: uuid.UUID) -> datetime | None:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT created_at FROM crypto.keys WHERE id = %s;",
                    (str(key_id),)
                )
                row = cur.fetchone()
                return row[0] if row else None
