# crypto/kem.py
import ctypes
from oqs import KeyEncapsulation

class KEMManager:
    @staticmethod
    def get_supported_kems():
        """
        Returns a static list of core KEM algorithms. 
        Bypasses the unstable liboqs-python discovery method to ensure stability.
        """
        return [
            "ML-KEM-512", 
            "ML-KEM-768", 
            "ML-KEM-1024", 
            "Kyber512", 
            "Kyber768", 
            "Kyber1024"
        ]

    @staticmethod
    def generate_keypair(algorithm_name):
        with KeyEncapsulation(algorithm_name) as kem:
            public_key = kem.generate_keypair()
            private_key = kem.export_secret_key()
            return {"public_key": public_key, "private_key": private_key}

    @staticmethod
    def encapsulate(algorithm_name, public_key):
        with KeyEncapsulation(algorithm_name) as kem:
            ciphertext, shared_secret = kem.encap_secret(public_key)
            return {"ciphertext": ciphertext, "shared_secret": shared_secret}

    @staticmethod
    def decapsulate(algorithm_name, ciphertext, private_key):
        with KeyEncapsulation(algorithm_name) as kem:
            kem.secret_key = (ctypes.c_uint8 * len(private_key)).from_buffer_copy(private_key)
            shared_secret = kem.decap_secret(ciphertext)
            return {"shared_secret": shared_secret}