# test_crypto.py
from crypto.kem import KEMManager

def run_kem_test(algo):
    print(f"\n--- Starting KEM Test for: {algo} ---")
    try:
        # 1. Generate keys
        keys = KEMManager.generate_keypair(algo)
        print(f"1. Keys generated. Public key length: {len(keys['public_key'])} bytes")

        # 2. Encapsulate (Sender)
        encap = KEMManager.encapsulate(algo, keys["public_key"])
        print("2. Encapsulation successful.")

        # 3. Decapsulate (Receiver)
        decap = KEMManager.decapsulate(algo, encap["ciphertext"], keys["private_key"])
        print("3. Decapsulation successful.")

        # 4. Verify
        if encap["shared_secret"] == decap["shared_secret"]:
            print("4. VERIFICATION SUCCESS: Shared secrets match!")
        else:
            print("4. VERIFICATION FAILURE: Shared secrets do not match.")
            
    except Exception as e:
        print(f"TEST FAILED: An error occurred: {e}")

if __name__ == "__main__":
    supported = KEMManager.get_supported_kems()
    print(f"Supported MVP KEM Algorithms: {supported}")
    
    # Run test on the NIST standard
    run_kem_test("ML-KEM-768")