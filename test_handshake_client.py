import socket
import struct

HOST = '127.0.0.1'
PORT = 5151
CLIENT_ID = b"test-client-1"

# We are sending dummy bytes here just to trigger the gateway's logic.
DUMMY_CIPHERTEXT = b"dummy_ciphertext_bytes_for_testing"

def send_length_prefixed(sock, data: bytes):
    """Packs the length of the data into 4 bytes, then sends the data."""
    sock.sendall(struct.pack('>I', len(data)))
    sock.sendall(data)

def main():
    print(f"🔌 Connecting to Gateway at {HOST}:{PORT}...")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print("✅ Connected successfully!")
            
            print(f"📤 Sending Client ID: {CLIENT_ID.decode()}")
            send_length_prefixed(s, CLIENT_ID)
            
            print("📤 Sending KEM Ciphertext...")
            send_length_prefixed(s, DUMMY_CIPHERTEXT)
            
            print("⏳ Waiting for Gateway response...")
            # The gateway replies with a 4-byte length, then the payload
            length_bytes = s.recv(4)
            if not length_bytes:
                print("❌ Connection closed by gateway before response.")
                return
                
            response_length = struct.unpack('>I', length_bytes)[0]
            response_data = s.recv(response_length)
            
            print("\n" + "="*50)
            print(f"📥 GATEWAY RESPONSE: {response_data.decode('utf-8', errors='replace')}")
            print("="*50 + "\n")
            
    except ConnectionRefusedError:
        print("❌ Connection refused. Is the FastAPI server running?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()