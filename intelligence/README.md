# Threat Intelligence Engine

**Standalone CVE Analysis, Threat Actor Profiling, and IOC Extraction Engine**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![GitHub](https://img.shields.io/github/stars/Amorleinis/threat-intelligence-engine?style=social)](https://github.com/Amorleinis/threat-intelligence-engine)

**By CyberGuard Industries - Lance Brady & AI Collaboration**

## Quick Access

<p align="center">
  <img src="repository_qr.png" alt="Scan to visit repository" width="200"/>
  <br>
  <em>Scan to visit this repository on GitHub</em>
</p>

## Overview

The Threat Intelligence Engine provides comprehensive threat intelligence capabilities including:
- CVE vulnerability analysis and scoring
- Threat actor profiling and tracking
- Indicator of Compromise (IOC) extraction
- Attack campaign correlation
- Integration with Neo4j graph database for relationship mapping

## Features

- ✅ **CVE Analysis**: Automated analysis of Common Vulnerabilities and Exposures
- ✅ **Threat Scoring**: ML-based threat severity scoring
- ✅ **IOC Extraction**: Automatic extraction of IPs, domains, URLs, file hashes
- ✅ **Threat Actor Profiling**: Track and profile threat actors and campaigns
- ✅ **Neo4j Integration**: Graph-based relationship mapping
- ✅ **Local Caching**: SQLite database for fast local queries

## Installation

### Prerequisites
- Python 3.8 or higher
- Neo4j database (optional, for graph features)

### Install from Source

```powershell
# Navigate to intelligence directory
cd c:\Users\allue\OneDrive\Desktop\datasets\intelligence

# Install the package
pip install -e .
```

### Install Dependencies Only

```powershell
pip install neo4j requests python-dateutil
```

## Quick Start

```python
from intelligence import ThreatIntelligenceEngine

# Initialize engine
engine = ThreatIntelligenceEngine(
    db_path="./data/intelligence.db",
    neo4j_uri="bolt://localhost:7687",  # Optional
    neo4j_user="neo4j",                  # Optional
    neo4j_password="password"            # Optional
)

# Analyze a CVE
cve_data = {
    "CVE_ID": "CVE-2024-1234",
    "description": "Remote code execution vulnerability",
    "severity": "CRITICAL",
    "cvss_score": 9.8,
    "published_date": "2024-01-15"
}

analysis = engine.analyze_cve(cve_data)
print(f"Threat Score: {analysis['threat_score']}")
print(f"IOCs found: {analysis['iocs']}")

# Search intelligence
results = engine.search_intelligence(query="CVE-2024-1234")

# Get metrics
metrics = engine.get_metrics()
print(f"Total CVEs analyzed: {metrics['total_cves_analyzed']}")

# Clean up
engine.close()
```

## API Reference

### `ThreatIntelligenceEngine(db_path, neo4j_uri=None, neo4j_user=None, neo4j_password=None)`

Initialize the intelligence engine.

**Parameters:**
- `db_path` (str): Path to SQLite database
- `neo4j_uri` (str, optional): Neo4j connection URI
- `neo4j_user` (str, optional): Neo4j username
- `neo4j_password` (str, optional): Neo4j password

### `analyze_cve(cve_data: dict) -> dict`

Analyze a CVE and extract threat intelligence.

**Returns:** Analysis with threat score, IOCs, and recommendations

### `extract_iocs(text: str) -> dict`

Extract indicators of compromise from text.

**Returns:** Dictionary with IP addresses, domains, URLs, and file hashes

### `search_intelligence(query: str, limit: int = 100) -> list`

Search intelligence database.

**Returns:** List of matching intelligence records

### `get_metrics() -> dict`

Get engine metrics and statistics.

## Configuration

Create a config file `intelligence_config.json`:

```json
{
  "db_path": "./data/intelligence.db",
  "neo4j": {
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "password": "your_password"
  },
  "cache_ttl": 3600,
  "max_cache_size": 10000
}
```

## Integration with Other Engines

The Intelligence Engine works standalone but can be integrated with:

- **Prevention Engine**: Feed extracted IOCs for blocking
- **Detection Engine**: Provide threat signatures for detection
- **Response Engine**: Supply threat context for incident response

```python
from intelligence import ThreatIntelligenceEngine
from prevention import ThreatPreventionEngine

# Analyze threat and block IOCs
intel = ThreatIntelligenceEngine(db_path="intel.db")
prev = ThreatPreventionEngine(db_path="prev.db")

analysis = intel.analyze_cve(cve_data)
for ip in analysis['iocs']['ip_addresses']:
    prev.block_ioc(ip, ioc_type="ip", severity="HIGH")
```

## Dependencies

- `neo4j>=4.4.0` - Neo4j graph database driver
- `requests>=2.26.0` - HTTP requests library
- `python-dateutil>=2.8.0` - Date utilities

## License

MIT License

## Support

For issues or questions, see the main platform documentation.
