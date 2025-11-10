"""
PLUG AND PLAY - Intelligence Engine Demo
Automatically loads real CVE data from your workspace and runs analysis
"""

import sys
import os
from pathlib import Path
import json

# Setup paths
base_dir = Path(__file__).parent
sys.path.insert(0, str(base_dir / "intelligence"))

print("=" * 80)
print("INTELLIGENCE ENGINE - PLUG AND PLAY DEMO")
print("=" * 80)
print()

# Find CVE data files
print("Scanning for CVE data files...")
cve_files = [
    base_dir / "cve_data_2020_2024_merged.json",
    base_dir / "cve_data.json",
    base_dir / "NVD" / "nvd_cve_processed.json",
    base_dir / "neo4j" / "nvd_cve_processed.json"
]

selected_file = None
for f in cve_files:
    if f.exists():
        selected_file = f
        print(f"✓ Found CVE data: {f.name}")
        break

if not selected_file:
    print("✗ No CVE data found. Please ensure CVE JSON files exist.")
    sys.exit(1)

print()

# Initialize Intelligence Engine
try:
    from threat_intelligence_engine import ThreatIntelligenceEngine
    
    print("Initializing Intelligence Engine...")
    os.makedirs("data/plug_and_play", exist_ok=True)
    
    engine = ThreatIntelligenceEngine(
        db_path="data/plug_and_play/intelligence.db",
        neo4j_uri=None  # Skip Neo4j for demo
    )
    print("✓ Intelligence Engine initialized")
    print()
    
    # Load and analyze real CVE data
    print(f"Loading CVE data from {selected_file.name}...")
    with open(selected_file, 'r', encoding='utf-8') as f:
        cve_data = json.load(f)
    
    # Handle different JSON formats
    if isinstance(cve_data, dict):
        if 'CVE_Items' in cve_data:
            cves = cve_data['CVE_Items'][:10]  # NVD format
        elif 'vulnerabilities' in cve_data:
            cves = cve_data['vulnerabilities'][:10]  # New NVD format
        else:
            cves = [cve_data]  # Single CVE
    elif isinstance(cve_data, list):
        cves = cve_data[:10]  # List of CVEs
    else:
        cves = []
    
    print(f"✓ Loaded {len(cves)} CVEs for analysis")
    print()
    
    # Analyze CVEs
    print("Analyzing CVEs...")
    print("-" * 80)
    
    analyzed_count = 0
    high_threats = 0
    
    for i, cve in enumerate(cves, 1):
        try:
            # Extract CVE ID from different formats
            cve_id = None
            if isinstance(cve, dict):
                cve_id = cve.get('CVE_ID') or cve.get('id') or cve.get('cve', {}).get('id')
                
                # Normalize to our format
                normalized_cve = {
                    'CVE_ID': cve_id or f'CVE-UNKNOWN-{i}',
                    'description': str(cve.get('description', cve.get('cve', {}).get('description', {}).get('description_data', [{}])[0].get('value', 'No description'))),
                    'severity': cve.get('severity', 'UNKNOWN'),
                    'cvss_score': float(cve.get('cvss_score', cve.get('impact', {}).get('baseMetricV3', {}).get('cvssV3', {}).get('baseScore', 0.0))),
                    'published_date': cve.get('published_date', cve.get('publishedDate', 'Unknown'))
                }
                
                analysis = engine.analyze_cve(normalized_cve)
                
                print(f"{i}. {analysis['cve_id']}")
                print(f"   Threat Score: {analysis['threat_score']:.2f}/10")
                print(f"   Severity: {analysis['severity']}")
                print(f"   IOCs found: {sum(len(v) for v in analysis['iocs'].values())}")
                
                analyzed_count += 1
                if analysis['threat_score'] >= 7.0:
                    high_threats += 1
                    
        except Exception as e:
            print(f"{i}. Error analyzing CVE: {e}")
    
    print("-" * 80)
    print()
    
    # Show metrics
    print("Analysis Summary:")
    print(f"  CVEs Analyzed: {analyzed_count}")
    print(f"  High Threats (score >= 7.0): {high_threats}")
    
    metrics = engine.get_metrics()
    print(f"  Total in Database: {metrics['total_cves_analyzed']}")
    print(f"  IOCs Extracted: {metrics['total_iocs_extracted']}")
    print()
    
    # Search example
    if analyzed_count > 0:
        print("Example: Searching intelligence database...")
        results = engine.search_intelligence(query="", limit=5)
        print(f"  Found {len(results)} recent entries")
        print()
    
    print("=" * 80)
    print("✓ INTELLIGENCE ENGINE DEMO COMPLETE")
    print("=" * 80)
    print()
    print("What you can do now:")
    print("  1. Check the database: data/plug_and_play/intelligence.db")
    print("  2. Run with more CVEs by modifying [:10] to [:100]")
    print("  3. Add Neo4j connection for graph analysis")
    print("  4. Integrate with Prevention Engine to block IOCs")
    print()
    
    engine.close()
    
except ImportError as e:
    print(f"✗ Intelligence Engine not available: {e}")
    print()
    print("To install:")
    print("  cd intelligence && pip install -e .")
    print("  OR run: .\\install_individual.ps1")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
