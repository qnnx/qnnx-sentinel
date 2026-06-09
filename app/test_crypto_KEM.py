def run_kem_test(algo):
    from crypto.kem import KEMManager

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
    try:
        from crypto.kem import KEMManager
    except RuntimeError as exc:
        print(f"SETUP ERROR: {exc}")
    else:
        supported = KEMManager.get_supported_kems()
        print(f"Supported MVP KEM Algorithms: {supported}")
        run_kem_test("ML-KEM-768")
