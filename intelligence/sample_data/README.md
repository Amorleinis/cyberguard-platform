# Sample Data for Intelligence Engine

This folder contains sample CVE data for testing and demonstration purposes.

## Files

- `cve_sample.json` - Sample CVE records with IOCs

## Usage

```python
import json
from pathlib import Path
from threat_intelligence_engine import ThreatIntelligenceEngine

# Load sample data
sample_file = Path(__file__).parent / "sample_data" / "cve_sample.json"
with open(sample_file) as f:
    cves = json.load(f)

# Initialize engine
engine = ThreatIntelligenceEngine(db_path="intel.db")

# Analyze CVEs
for cve in cves:
    analysis = engine.analyze_cve(cve)
    print(f"Analyzed {cve['cve_id']}: Severity {analysis['severity']}")
```

## Data Format

```json
{
  "cve_id": "CVE-YYYY-NNNN",
  "description": "Vulnerability description",
  "published_date": "YYYY-MM-DD",
  "cvss_score": 0.0,
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "affected_products": ["Product Name"],
  "attack_vector": "NETWORK|ADJACENT|LOCAL|PHYSICAL",
  "iocs": {
    "ip_addresses": [],
    "domains": [],
    "urls": [],
    "file_hashes": []
  }
}
```
