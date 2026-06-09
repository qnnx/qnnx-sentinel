# test_crypto.py
from crypto.kem import KEMManager
from crypto.dsa import DSAManager

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
def run_dsa_test(algo):
    print(f"\n--- Starting DSA Test for: {algo} ---")
    try:
        # The data we want to protect
        original_message = b"Sentinel PQC Authorization Request - ID: 1045"
        tampered_message = b"Sentinel PQC Authorization Request - ID: 9999"

        # 1. Generate keys
        keys = DSAManager.generate_keypair(algo)
        print(f"1. Keys generated. Public key length: {len(keys['public_key'])} bytes")

        # 2. Sign the original message
        sig_data = DSAManager.sign(algo, original_message, keys["private_key"])
        print(f"2. Message signed. Signature length: {len(sig_data['signature'])} bytes")

        # 3. Verify with the original message (Should be True)
        ver_good = DSAManager.verify(algo, original_message, sig_data["signature"], keys["public_key"])
        print(f"3. Verification against original message: {ver_good['is_valid']}")

        # 4. Verify with the tampered message (Should be False)
        ver_bad = DSAManager.verify(algo, tampered_message, sig_data["signature"], keys["public_key"])
        print(f"4. Verification against tampered message: {ver_bad['is_valid']}")

        # 5. Final check
        if ver_good["is_valid"] and not ver_bad["is_valid"]:
            print("5. VERIFICATION SUCCESS: The signature engine caught the tamper attempt!")
        else:
            print("5. VERIFICATION FAILURE: Engine behavior is incorrect.")
            
    except Exception as e:
        print(f"TEST FAILED: An error occurred: {e}")

if __name__ == "__main__":
    # Run the KEM test
    print(f"Supported KEMs: {KEMManager.get_supported_kems()}")
    run_kem_test("ML-KEM-768")
    
    # Run the DSA test
    print(f"\nSupported DSAs: {DSAManager.get_supported_dsas()}")
    run_dsa_test("ML-DSA-65")