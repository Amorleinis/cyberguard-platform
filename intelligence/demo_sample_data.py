# Quick Demo - Intelligence Engine with Sample Data

import json
from pathlib import Path
from threat_intelligence_engine import ThreatIntelligenceEngine

def run_demo():
    print("="*80)
    print("INTELLIGENCE ENGINE - SAMPLE DATA DEMO")
    print("="*80)
    print()
    
    # Load sample CVE data
    sample_file = Path(__file__).parent / "sample_data" / "cve_sample.json"
    
    if not sample_file.exists():
        print(f"Error: Sample data not found at {sample_file}")
        return
    
    with open(sample_file) as f:
        cves = json.load(f)
    
    print(f"Loaded {len(cves)} sample CVEs")
    print()
    
    # Initialize engine
    engine = ThreatIntelligenceEngine(db_path=":memory:")  # Use in-memory DB for demo
    print("Intelligence Engine initialized")
    print()
    
    # Analyze each CVE
    print("Analyzing CVEs...")
    print("-"*80)
    
    for cve in cves:
        print(f"\n{cve['cve_id']}")
        print(f"  Severity: {cve['severity']}")
        print(f"  CVSS Score: {cve['cvss_score']}")
        print(f"  Affected Products: {', '.join(cve['affected_products'])}")
        
        # Extract IOCs
        iocs = cve.get('iocs', {})
        total_iocs = (
            len(iocs.get('ip_addresses', [])) +
            len(iocs.get('domains', [])) +
            len(iocs.get('urls', [])) +
            len(iocs.get('file_hashes', []))
        )
        print(f"  IOCs Found: {total_iocs}")
        
        if iocs.get('ip_addresses'):
            print(f"    IPs: {', '.join(iocs['ip_addresses'])}")
        if iocs.get('domains'):
            print(f"    Domains: {', '.join(iocs['domains'])}")
    
    print()
    print("="*80)
    print("Demo complete! Sample data analyzed successfully.")
    print("="*80)

if __name__ == "__main__":
    run_demo()
