import base64
import sys

from crypto.kem import KEMManager

algorithm = sys.argv[1] if len(sys.argv) > 1 else "ML-KEM-768"

keys = KEMManager.generate_keypair(algorithm)
public_key = keys["public_key"]
private_key = keys["private_key"]

print(f"Algorithm:  {algorithm}")
print(f"Public key  ({len(public_key)} bytes):")
print(public_key.hex())
print()
print(f"Private key ({len(private_key)} bytes):")
print(private_key.hex())

with open(f"{algorithm}_public.key", "wb") as f:
    f.write(base64.b64encode(public_key))
with open(f"{algorithm}_private.key", "wb") as f:
    f.write(base64.b64encode(private_key))

print()
print(f"Saved base64-encoded keys to {algorithm}_public.key and {algorithm}_private.key")
