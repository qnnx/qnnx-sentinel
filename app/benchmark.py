import time
import csv
import sys
import os

# --- STRUCTURE PATHING FIX ---
# This ensures Python can find the 'crypto' folder even if you run this 
# script from the root 'internship' folder instead of the 'app' folder.
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = current_dir if os.path.basename(current_dir) == 'app' else os.path.join(current_dir, 'app')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# Now we can safely import from your new structure
from crypto.kem import KEMManager
from crypto.dsa import DSAManager

# Configuration
ITERATIONS = 1000
CSV_FILENAME = "pqc_performance_metrics.csv"

def benchmark_kem(kem_name, iterations):
    print(f"]Benchmarking KEM: {kem_name} ({iterations} iterations)...")
    results = []

    # 1. Key Generation
    start = time.perf_counter()
    for _ in range(iterations):
        keys = KEMManager.generate_keypair(kem_name)
    avg_keygen_ms = ((time.perf_counter() - start) / iterations) * 1000
    results.append([kem_name, "KEM", "Key Generation", round(avg_keygen_ms, 4)])

    # We need one valid keypair for the next steps
    keys = KEMManager.generate_keypair(kem_name)
    public_key = keys["public_key"]
    private_key = keys["private_key"]

    # 2. Encapsulation
    start = time.perf_counter()
    for _ in range(iterations):
        encap = KEMManager.encapsulate(kem_name, public_key)
    avg_encap_ms = ((time.perf_counter() - start) / iterations) * 1000
    results.append([kem_name, "KEM", "Encapsulation", round(avg_encap_ms, 4)])

    # We need one valid ciphertext for decapsulation
    encap = KEMManager.encapsulate(kem_name, public_key)
    ciphertext = encap["ciphertext"]

    # 3. Decapsulation
    start = time.perf_counter()
    for _ in range(iterations):
        decap = KEMManager.decapsulate(kem_name, ciphertext, private_key)
    avg_decap_ms = ((time.perf_counter() - start) / iterations) * 1000
    results.append([kem_name, "KEM", "Decapsulation", round(avg_decap_ms, 4)])

    return results

def benchmark_dsa(dsa_name, iterations):
    print(f"Benchmarking DSA: {dsa_name} ({iterations} iterations)...")
    results = []
    message = b"Sentinel system benchmark test message payload"

    # 1. Key Generation
    start = time.perf_counter()
    for _ in range(iterations):
        keys = DSAManager.generate_keypair(dsa_name)
    avg_keygen_ms = ((time.perf_counter() - start) / iterations) * 1000
    results.append([dsa_name, "DSA", "Key Generation", round(avg_keygen_ms, 4)])

    # We need one valid keypair for signing
    keys = DSAManager.generate_keypair(dsa_name)
    public_key = keys["public_key"]
    private_key = keys["private_key"]

    # 2. Signing
    start = time.perf_counter()
    for _ in range(iterations):
        sig_data = DSAManager.sign(dsa_name, message, private_key)
    avg_sign_ms = ((time.perf_counter() - start) / iterations) * 1000
    results.append([dsa_name, "DSA", "Sign", round(avg_sign_ms, 4)])

    # We need one valid signature for verification
    sig_data = DSAManager.sign(dsa_name, message, private_key)
    signature = sig_data["signature"] if isinstance(sig_data, dict) else sig_data

    # 3. Verification
    start = time.perf_counter()
    for _ in range(iterations):
        is_valid = DSAManager.verify(dsa_name, message, signature, public_key)
    avg_verify_ms = ((time.perf_counter() - start) / iterations) * 1000
    results.append([dsa_name, "DSA", "Verify", round(avg_verify_ms, 4)])

    return results

def run_benchmarks():
    
    all_metrics = []

    # Using the standardized names from NIST/liboqs
    target_kems = ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]
    target_dsas = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]

    # Run KEM Benchmarks
    for kem in target_kems:
        try:
            metrics = benchmark_kem(kem, ITERATIONS)
            all_metrics.extend(metrics)
        except Exception as e:
            print(f"Error benchmarking {kem}: {e}")


    # Run DSA Benchmarks
    for dsa in target_dsas:
        try:
            metrics = benchmark_dsa(dsa, ITERATIONS)
            all_metrics.extend(metrics)
        except Exception as e:
            print(f"Error benchmarking {dsa}: {e}")

    # Export to CSV inside the app directory
    csv_path = os.path.join(app_dir, CSV_FILENAME)
    print(f"\nExporting results to {csv_path}...")
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Algorithm", "Type", "Operation", "Time_ms"])
        writer.writerows(all_metrics)

    print("Benchmarking complete! Data is ready for analysis.")

if __name__ == "__main__":
    run_benchmarks()