import secrets
import uuid
from app.utils.crypto import sha256_hex

def main():
    # 1. Generate the raw, secure API key
    raw_api_key = f"qnnx_{secrets.token_hex(20)}"
    
    # 2. Hash it using your app's exact crypto utility
    hashed_key = sha256_hex(raw_api_key)
    
    # 3. Generate a UUID for the new key row
    key_id = uuid.uuid4()

    print("\n" + "="*65)
    print("🚀 API KEY GENERATED SUCCESSFULLY (OFFLINE MODE) 🚀")
    print("="*65)
    print(f"RAW API KEY:  {raw_api_key}")
    print("⚠️ SAVE THIS NOW. You will never be able to see it again! ⚠️")
    print("="*65 + "\n")
    
    print("STEP 2: Copy the SQL below and run it in the Supabase SQL Editor:\n")
    print("-" * 65)
    print(f"""
INSERT INTO api_keys (id, user_id, name, key_hash, status)
VALUES (
    '{key_id}', 
    (SELECT id FROM users LIMIT 1), 
    'VPN Gateway Main Token', 
    '{hashed_key}', 
    'active'
);
    """.strip())
    print("-" * 65 + "\n")

if __name__ == "__main__":
    main()