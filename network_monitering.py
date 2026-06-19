import psutil
import requests
import time
import json
from datetime import datetime

class NetworkMonitor:
    def __init__(self, check_interval=5):
        """Initializes the monitor to check metrics every X seconds."""
        self.check_interval = check_interval
        self.net_io_start = psutil.net_io_counters()

    def get_public_ip(self):
        """Fetches the current public IP."""
        try:
            response = requests.get('https://api.ipify.org', timeout=5)
            if response.status_code == 200:
                return response.text.strip()
        except requests.RequestException:
            pass
        return "Offline/Unreachable"

    def get_connection_stats(self):
        """Gathers active connection count and unique destination IPs."""
        try:
            connections = psutil.net_connections(kind='inet')
            established = [conn for conn in connections if conn.status == 'ESTABLISHED']
            
            # Extract unique destination IPs using a set
            dest_ips = list(set(conn.raddr.ip for conn in established if conn.raddr))
            
            return len(established), dest_ips
        except psutil.AccessDenied:
            return 0, ["Requires Admin Privileges"]

    def get_bandwidth(self):
        """Calculates upload and download speeds (KB/s)."""
        net_io_end = psutil.net_io_counters()
        
        # Calculate bytes transferred over the interval
        bytes_sent = net_io_end.bytes_sent - self.net_io_start.bytes_sent
        bytes_recv = net_io_end.bytes_recv - self.net_io_start.bytes_recv
        
        # Convert to KB/s
        kb_sent_per_sec = (bytes_sent / 1024) / self.check_interval
        kb_recv_per_sec = (bytes_recv / 1024) / self.check_interval
        
        # Reset baseline for next calculation
        self.net_io_start = net_io_end
        
        return round(kb_sent_per_sec, 2), round(kb_recv_per_sec, 2)

    def run(self):
        """Main loop that generates and pushes structured logs."""
        print("Starting Network Monitoring Module... (Press Ctrl+C to stop)")
        print("-" * 60)
        
        try:
            while True:
                # Wait for the interval to calculate speed accurately
                time.sleep(self.check_interval)
                
                # Gather all metrics
                public_ip = self.get_public_ip()
                up_kbps, down_kbps = self.get_bandwidth()
                active_count, dest_ips = self.get_connection_stats()
                
                # Construct the structured JSON log
                log_entry = {
                    "timestamp": datetime.now().isoformat(),
                    "module": "network_telemetry",
                    "public_ip": public_ip,
                    "metrics": {
                        "upload_kbps": up_kbps,
                        "download_kbps": down_kbps,
                        "active_connections": active_count
                    },
                    "destination_ips": dest_ips
                }
                
                # Output the JSON log
                # In production, this would be pushed via an API to your Layer 5 Dashboard
                print(json.dumps(log_entry))
                
        except KeyboardInterrupt:
            print("\nMonitoring Module Offline.")

if __name__ == "__main__":
    # Initialize the module to log data every 3 seconds
    module = NetworkMonitor(check_interval=3)
    module.run()