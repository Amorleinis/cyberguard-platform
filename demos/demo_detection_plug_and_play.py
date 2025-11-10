"""
PLUG AND PLAY - Detection Engine Demo
Automatically loads real threat data and performs detection
"""

import sys
import os
from pathlib import Path
import json
from datetime import datetime

# Setup paths
base_dir = Path(__file__).parent
sys.path.insert(0, str(base_dir / "detection"))

print("=" * 80)
print("DETECTION ENGINE - PLUG AND PLAY DEMO")
print("=" * 80)
print()

# Find threat data files
print("Scanning for threat data files...")
data_files = [
    base_dir / "DATAX" / "data" / "processed" / "enriched_cyber_threats_scored.json",
    base_dir / "neo4j" / "graph" / "NVD" / "data" / "zeek_logs.json",
    base_dir / "data" / "enriched_results.json"
]

selected_file = None
for f in data_files:
    if f.exists():
        selected_file = f
        print(f"✓ Found threat data: {f.name}")
        break

if not selected_file:
    print("⚠ No pre-built threat data found. Creating sample events...")
    events = [
        {
            "timestamp": datetime.now().isoformat(),
            "source_ip": "192.168.1.100",
            "dest_ip": "10.0.0.50",
            "port": 4444,
            "bytes_sent": 1024000,
            "event_type": "suspicious_connection",
            "protocol": "TCP"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "source_ip": "10.0.0.75",
            "dest_ip": "8.8.8.8",
            "port": 53,
            "bytes_sent": 512,
            "event_type": "dns_query",
            "protocol": "UDP"
        },
        {
            "timestamp": datetime.now().isoformat(),
            "source_ip": "192.168.1.200",
            "dest_ip": "172.16.0.10",
            "port": 22,
            "bytes_sent": 2048,
            "event_type": "ssh_connection",
            "protocol": "TCP"
        }
    ]
else:
    # Load real threat data
    print(f"Loading threat data from {selected_file.name}...")
    with open(selected_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract events from different formats
    if isinstance(data, list):
        events = data[:5]
    elif isinstance(data, dict) and 'events' in data:
        events = data['events'][:5]
    else:
        events = [data]
    
    print(f"✓ Loaded {len(events)} events")

print()

# Initialize Detection Engine
try:
    from threat_detection_engine import ThreatDetectionEngine
    
    print("Initializing Detection Engine...")
    os.makedirs("data/plug_and_play", exist_ok=True)
    
    engine = ThreatDetectionEngine(db_path="data/plug_and_play/detection.db")
    print("✓ Detection Engine initialized")
    print()
    
    # Analyze events
    print("Analyzing security events...")
    print("-" * 80)
    
    threats_detected = 0
    total_analyzed = 0
    
    for i, event in enumerate(events, 1):
        try:
            # Normalize event format
            normalized_event = {
                "timestamp": event.get('timestamp', datetime.now().isoformat()),
                "source_ip": event.get('source_ip', event.get('src_ip', 'unknown')),
                "dest_ip": event.get('dest_ip', event.get('dst_ip', 'unknown')),
                "port": event.get('port', event.get('dest_port', 0)),
                "event_type": event.get('event_type', event.get('type', 'unknown')),
                "bytes_sent": event.get('bytes_sent', event.get('bytes', 0))
            }
            
            detection = engine.analyze_event(normalized_event)
            
            threat_icon = "🚨" if detection.get('is_threat') else "✓"
            print(f"{threat_icon} Event {i}: {normalized_event['source_ip']} → {normalized_event['dest_ip']}:{normalized_event['port']}")
            print(f"   Type: {normalized_event['event_type']}")
            print(f"   Threat: {detection.get('is_threat', False)}")
            print(f"   Confidence: {detection.get('confidence', 0):.2%}")
            print(f"   Method: {detection.get('detection_method', 'unknown')}")
            
            total_analyzed += 1
            if detection.get('is_threat'):
                threats_detected += 1
                
        except Exception as e:
            print(f"✗ Event {i}: Error - {e}")
    
    print("-" * 80)
    print()
    
    # Show metrics
    print("Detection Summary:")
    print(f"  Events Analyzed: {total_analyzed}")
    print(f"  Threats Detected: {threats_detected}")
    print(f"  Detection Rate: {(threats_detected/total_analyzed*100) if total_analyzed > 0 else 0:.1f}%")
    
    metrics = engine.get_metrics()
    print(f"  Total Events in DB: {metrics.get('total_events_analyzed', 0)}")
    print(f"  Total Threats in DB: {metrics.get('total_threats_detected', 0)}")
    print()
    
    print("=" * 80)
    print("✓ DETECTION ENGINE DEMO COMPLETE")
    print("=" * 80)
    print()
    print("What you can do now:")
    print("  1. Check the database: data/plug_and_play/detection.db")
    print("  2. Add more event sources (SIEM, network logs)")
    print("  3. Integrate with Response Engine for auto-response")
    print("  4. Train custom ML models on your data")
    print()
    
    engine.close()
    
except ImportError as e:
    print(f"✗ Detection Engine not available: {e}")
    print()
    print("To install:")
    print("  cd detection && pip install -e .")
    print("  pip install pandas numpy scikit-learn torch")
    print("  OR run: .\\install_individual.ps1")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
