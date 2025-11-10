# Threat Isolation Engine

**Standalone Network Segmentation and Host Quarantine**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![GitHub](https://img.shields.io/github/stars/Amorleinis/threat-isolation-engine?style=social)](https://github.com/Amorleinis/threat-isolation-engine)

**By CyberGuard Industries - Lance Brady & AI Collaboration**

## Quick Access

<p align="center">
  <img src="repository_qr.png" alt="Scan to visit repository" width="200"/>
  <br>
  <em>Scan to visit this repository on GitHub</em>
</p>

## Overview

The Threat Isolation Engine provides isolation capabilities including:
- Network segmentation and VLAN isolation
- Host quarantine and containment
- User access restriction
- Container isolation
- Automated rollback

## Features

- ✅ **Network Isolation**: VLAN and subnet segmentation
- ✅ **Host Quarantine**: Isolate compromised systems
- ✅ **User Restrictions**: Limit user access during incidents
- ✅ **Container Isolation**: Isolate containerized workloads
- ✅ **Monitoring**: Track isolated resources

## Installation

```powershell
cd c:\Users\allue\OneDrive\Desktop\datasets\isolation
pip install -e .
```

## Quick Start

```python
from isolation import ThreatIsolationEngine

engine = ThreatIsolationEngine()

# Isolate a host
result = engine.isolate_host(
    hostname="workstation-123",
    reason="Malware detected",
    severity="HIGH",
    duration_hours=24
)

engine.close()
```

## License

MIT License
