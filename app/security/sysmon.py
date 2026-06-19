import win32evtlog
import time
import xml.etree.ElementTree as ET
from app.security.alert import hids_engine
import logging
logger = logging.getLogger("QNNX_HIDS")

def poll_windows_sysmon():
    """Continuously reads the Windows Sysmon event log and feeds the HIDS engine."""
    server = 'localhost'
    log_type = 'Microsoft-Windows-Sysmon/Operational'
    
    # Open the event log starting from the end
    flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
    hand = win32evtlog.OpenEventLog(server, log_type)

    print("[*] HIDS Windows Sysmon Bridge Active...")
    
    try:
        while True:
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            if not events:
                time.sleep(1) # Wait for new logs
                continue

            for event in events:
                event_id = event.EventID & 0xFFFF
                
                # We only care about Process Creation (1) and Network Connections (3)
                if event_id not in [1, 3]:
                    continue
                
                # Windows Event Data is stored as XML strings, we parse it into a dict
                xml_content = win32evtlog.EvtRender(None, event, win32evtlog.EvtRenderEventXml)
                root = ET.fromstring(xml_content)
                
                # Extract event data payload into a clean dictionary
                ns = {'e': 'http://schemas.microsoft.com/win/2004/08/events/event'}
                event_data = {}
                for data in root.findall('.//e:EventData/e:Data', ns):
                    name = data.get('Name')
                    text = data.text
                    if name and text:
                        event_data[name] = text
                        
                # Feed the parsed Windows Event into our IDS Engine
                hids_engine.process_windows_event(event_id, event_data)
                
    except Exception as e:
        logger.error(f"Sysmon bridge failed: {e}")
    finally:
        win32evtlog.CloseEventLog(hand)