import time
from app.security.alert import hids_engine

print("--- Starting QNNX-Sentinel Threat Simulation ---\n")

# ---------------------------------------------------------
# Test 1: API Layer Brute-Force (Credential Stuffing)
# ---------------------------------------------------------
print("[*] Injecting 6 failed API auth attempts from 192.168.1.50...")
for i in range(6):
    hids_engine.process_api_event(
        event_type="INVALID_API_KEY",
        ip_address="192.168.1.50",
        details={"attempt": i + 1, "note": "Simulated brute force"}
    )
    time.sleep(0.1) # Brief pause between requests


# ---------------------------------------------------------
# Test 2: Host Layer - Remote Code Execution (RCE)
# ---------------------------------------------------------
print("\n[*] Simulating compromised web worker spawning a reverse shell...")
hids_engine.process_windows_event(
    event_id=1,
    event_data={
        "ParentImage": "C:\\Users\\Somil\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
        "Image": "C:\\Windows\\System32\\cmd.exe",
        "CommandLine": "cmd.exe /c whoami"
    }
)


# ---------------------------------------------------------
# Test 3: Host Layer - Unauthorized C2 Outbound Connection
# ---------------------------------------------------------
print("\n[*] Simulating backend attempting to connect to external attacker IP...")
hids_engine.process_windows_event(
    event_id=3,
    event_data={
        "Initiated": "true",
        "Image": "C:\\Users\\Somil\\AppData\\Local\\Programs\\Python\\Python311\\python.exe",
        "SourceIp": "192.168.1.15",
        "DestinationIp": "142.250.190.46", # A random public IP not in your whitelist
        "DestinationPort": "4444"
    }
)


# ---------------------------------------------------------
# Test 4: Host Layer - Inbound Vertical Port Scan
# ---------------------------------------------------------
print("\n[*] Simulating Nmap vertical port scan from 10.0.0.99...")
# We hit 16 unique ports (Threshold is 15)
for port in range(8000, 8016):
    hids_engine.process_windows_event(
        event_id=3,
        event_data={
            "Initiated": "false",
            "Image": "System",
            "SourceIp": "10.0.0.99",
            "DestinationIp": "192.168.1.15",
            "DestinationPort": str(port)
        }
    )
    time.sleep(0.05)

# ---------------------------------------------------------
# Test 5: VPN IP Change and Heartbeat Loss
# ---------------------------------------------------------
print("\n[*] Simulating VPN Tunnel Up...")
hids_engine.process_vpn_event("TUNNEL_UP", peer_id="admin_laptop_01", ip_address="203.0.113.5")

print("[*] Simulating VPN Peer roaming to a new IP address...")
hids_engine.process_vpn_event("ENDPOINT_IP_CHANGE", peer_id="admin_laptop_01", ip_address="198.51.100.22")

print("[*] Simulating Dead Peer Detection (Heartbeat Loss)...")
hids_engine.process_vpn_event("HEARTBEAT_LOSS", peer_id="admin_laptop_01")


# ---------------------------------------------------------
# Test 6: Physical Threat - Unauthorized USB Insertion
# ---------------------------------------------------------
print("\n[*] Simulating unauthorized USB drive plugged into the production server...")
hids_engine.process_hardware_event(
    event_type="USB_INSERTION",
    device_name="SanDisk Cruzer Glide USB Device",
    details={
        "Vendor": "SanDisk",
        "Volume": "E:\\",
        "EventID": "4663"
    }
)

print("\n--- Simulation Complete ---")