import ctypes

from app.crypto._oqs_loader import load_signature

class DSAManager:
    @staticmethod
    def get_supported_dsas():
        """
        Returns a static list of core DSA algorithms.
        Bypasses the unstable liboqs-python discovery method.
        """
        return [
            "ML-DSA-44", 
            "ML-DSA-65", 
            "ML-DSA-87",
            "Dilithium2",
            "Dilithium3",
            "Dilithium5"
        ]

    @staticmethod
    def generate_keypair(algorithm_name):
        """Generates a signing keypair."""
        Signature = load_signature()
        with Signature(algorithm_name) as signer:
            public_key = signer.generate_keypair()
            private_key = signer.export_secret_key()
            return {"public_key": public_key, "private_key": private_key}

    @staticmethod
    def sign(algorithm_name, message: bytes, private_key: bytes):
        """
        Signs a byte message using the provided private key.
        """
        Signature = load_signature()
        with Signature(algorithm_name) as signer:
            # The exact same ctypes bridge we used in KEM
            signer.secret_key = (ctypes.c_uint8 * len(private_key)).from_buffer_copy(private_key)
            signature = signer.sign(message)
            return {"signature": signature}

    @staticmethod
    def verify(algorithm_name, message: bytes, signature: bytes, public_key: bytes):
        """
        Verifies that a signature is valid for a given message and public key.
        """
        Signature = load_signature()
        with Signature(algorithm_name) as verifier:
            # verify() returns a simple boolean (True/False)
            is_valid = verifier.verify(message, signature, public_key)
            return {"is_valid": is_valid}
