"""
Example: Using the Unified Bundle
Demonstrates using all engines together through the orchestrator
"""

import sys
from pathlib import Path

# Add to path if not installed
sys.path.insert(0, str(Path(__file__).parent))

# OPTION 1: Import from unified bundle (if installed with pip install -e .)
# from threat_intelligence_platform import ThreatIntelligencePlatform

# OPTION 2: Direct import (without pip install)
sys.path.insert(0, str(Path(__file__).parent / "orchestration"))
from threat_platform_orchestrator import ThreatIntelligencePlatform

def main():
    print("=" * 80)
    print("UNIFIED BUNDLE EXAMPLE - All Engines Together")
    print("=" * 80)
    print()
    
    # Initialize the complete platform
    print("Initializing Threat Intelligence Platform...")
    platform = ThreatIntelligencePlatform(base_dir="./data/unified_example")
    print("✓ Platform initialized with all 7 engines")
    print()
    
    # Example 1: Process a malware detection alert
    print("Example 1: Processing malware detection alert...")
    malware_alert = {
        "type": "malware_detection",
        "severity": "HIGH",
        "source": "endpoint_protection",
        "details": {
            "host": "workstation-123",
            "malware_family": "Trojan.GenericKD",
            "file_hash": "5d41402abc4b2a76b9719d911017c592",
            "file_path": "C:\\Users\\user\\Downloads\\malware.exe"
        }
    }
    
    try:
        result = platform.handle_malware_detection(malware_alert)
        print(f"✓ Malware handled: {result}")
    except Exception as e:
        print(f"⚠ Malware handling (deps needed): {e}")
    print()
    
    # Example 2: Process a data breach
    print("Example 2: Processing data breach...")
    breach_alert = {
        "affected_systems": ["database-server-01", "web-server-02"],
        "data_types": ["customer_pii", "credentials"],
        "severity": "CRITICAL",
        "estimated_records": 50000
    }
    
    try:
        result = platform.handle_data_breach(breach_alert)
        print(f"✓ Breach handled: {result}")
    except Exception as e:
        print(f"⚠ Breach handling (deps needed): {e}")
    print()
    
    # Example 3: Get platform status
    print("Example 3: Getting platform status...")
    try:
        status = platform.get_platform_status()
        print(f"✓ Platform Status:")
        print(f"  - Status: {status.get('platform_status', 'Unknown')}")
        print(f"  - Active Engines: {status.get('active_engines', 0)}")
        print(f"  - Uptime: {status.get('uptime_seconds', 0):.2f} seconds")
    except Exception as e:
        print(f"⚠ Status check (deps needed): {e}")
    print()
    
    # Shutdown
    print("Shutting down platform...")
    platform.shutdown()
    print("✓ Platform shut down successfully")
    print()
    
    print("=" * 80)
    print("UNIFIED BUNDLE BENEFITS:")
    print("- All engines work together seamlessly")
    print("- Centralized configuration")
    print("- Automatic workflow orchestration")
    print("- Unified metrics and reporting")
    print("=" * 80)

if __name__ == "__main__":
    main()
