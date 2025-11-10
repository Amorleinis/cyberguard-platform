# Threat Prevention Engine

**Standalone IOC Blocking, Vulnerability Patching, and Attack Surface Monitoring**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![GitHub](https://img.shields.io/github/stars/Amorleinis/threat-prevention-engine?style=social)](https://github.com/Amorleinis/threat-prevention-engine)

**By CyberGuard Industries - Lance Brady & AI Collaboration**

## Quick Access

<p align="center">
  <img src="repository_qr.png" alt="Scan to visit repository" width="200"/>
  <br>
  <em>Scan to visit this repository on GitHub</em>
</p>

## Overview

The Threat Prevention Engine provides proactive threat prevention capabilities including:
- Indicator of Compromise (IOC) blocking
- Vulnerability patch management
- Attack surface monitoring
- Prevention rule management
- Threat hunting capabilities

## Features

- ✅ **IOC Blocking**: Block malicious IPs, domains, URLs, and file hashes
- ✅ **Prevention Rules**: Create and manage prevention policies
- ✅ **Patch Management**: Track and deploy vulnerability patches
- ✅ **Attack Surface Monitoring**: Monitor exposed services and vulnerabilities
- ✅ **Threat Hunting**: Proactive threat discovery
- ✅ **Metrics & Reporting**: Track prevention effectiveness

## Installation

### Prerequisites
- Python 3.8 or higher

### Install from Source

```powershell
# Navigate to prevention directory
cd c:\Users\allue\OneDrive\Desktop\datasets\prevention

# Install the package
pip install -e .
```

### Install Dependencies Only

```powershell
pip install requests python-dateutil
```

## Quick Start

```python
from prevention import ThreatPreventionEngine

# Initialize engine
engine = ThreatPreventionEngine(db_path="./data/prevention.db")

# Block a malicious IP
result = engine.block_ioc(
    ioc_value="192.168.1.100",
    ioc_type="ip",
    source="threat_intel",
    severity="HIGH",
    description="Known C2 server"
)

# Create prevention rule
rule = engine.create_prevention_rule(
    rule_name="Block Tor Exit Nodes",
    rule_type="network",
    conditions={"source": "tor_exit_nodes"},
    action="block",
    severity="MEDIUM"
)

# Manage patches
patch = engine.create_patch(
    patch_id="MS-2024-001",
    vulnerability_ids=["CVE-2024-1234"],
    patch_name="January Security Update",
    severity="CRITICAL"
)

# Get metrics
metrics = engine.get_metrics()
print(f"Total IOCs blocked: {metrics['total_iocs_blocked']}")

# Clean up
engine.close()
```

## API Reference

### `ThreatPreventionEngine(db_path: str)`

Initialize the prevention engine.

### `block_ioc(ioc_value: str, ioc_type: str, source: str, severity: str) -> bool`

Block an indicator of compromise.

**IOC Types:** `ip`, `domain`, `url`, `file_hash`, `email`

### `create_prevention_rule(rule_name: str, rule_type: str, conditions: dict, action: str) -> dict`

Create a prevention rule.

### `create_patch(patch_id: str, vulnerability_ids: list, patch_name: str, severity: str) -> dict`

Create a patch record.

### `monitor_attack_surface() -> dict`

Scan and monitor attack surface.

## Integration Example

```python
from intelligence import ThreatIntelligenceEngine
from prevention import ThreatPreventionEngine

# Intel -> Prevention workflow
intel = ThreatIntelligenceEngine(db_path="intel.db")
prev = ThreatPreventionEngine(db_path="prev.db")

# Analyze CVE and auto-block IOCs
analysis = intel.analyze_cve(cve_data)
for ip in analysis['iocs']['ip_addresses']:
    prev.block_ioc(ip, ioc_type="ip", severity="HIGH", source="cve_analysis")
```

## License

MIT License
