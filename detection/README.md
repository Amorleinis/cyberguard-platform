# Threat Detection Engine

**Standalone ML-Powered Threat Detection with Multi-Method Analysis**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![GitHub](https://img.shields.io/github/stars/Amorleinis/threat-detection-engine?style=social)](https://github.com/Amorleinis/threat-detection-engine)

**By CyberGuard Industries - Lance Brady & AI Collaboration**

## Quick Access

<p align="center">
  <img src="repository_qr.png" alt="Scan to visit repository" width="200"/>
  <br>
  <em>Scan to visit this repository on GitHub</em>
</p>

## Overview

The Threat Detection Engine provides advanced threat detection using:
- Machine learning-based anomaly detection
- Signature-based detection
- Behavioral analysis
- Graph-based correlation
- Real-time event processing

## Features

- ✅ **Neural Network Detection**: PyTorch-based deep learning
- ✅ **Signature Matching**: Pattern-based threat detection
- ✅ **Behavioral Analysis**: Detect anomalous behavior patterns
- ✅ **Graph Correlation**: Network relationship analysis
- ✅ **Real-time Processing**: Continuous event stream analysis
- ✅ **Multi-method Fusion**: Combine multiple detection techniques

## Installation

### Prerequisites
- Python 3.8 or higher

### Install from Source

```powershell
# Navigate to detection directory
cd c:\Users\allue\OneDrive\Desktop\datasets\detection

# Install the package
pip install -e .
```

### Install Dependencies

```powershell
pip install numpy pandas scikit-learn torch networkx
```

## Quick Start

```python
from detection import ThreatDetectionEngine

# Initialize engine
engine = ThreatDetectionEngine(db_path="./data/detection.db")

# Analyze an event
event = {
    "timestamp": "2024-01-15T10:30:00",
    "source_ip": "10.0.0.50",
    "dest_ip": "192.168.1.100",
    "port": 4444,
    "bytes_sent": 1024,
    "event_type": "network_connection"
}

detection = engine.analyze_event(event)
print(f"Is Threat: {detection['is_threat']}")
print(f"Confidence: {detection['confidence']}")
print(f"Method: {detection['detection_method']}")

# Get metrics
metrics = engine.get_metrics()

# Clean up
engine.close()
```

## API Reference

### `ThreatDetectionEngine(db_path: str)`

Initialize the detection engine.

### `analyze_event(event: dict) -> dict`

Analyze a security event for threats.

**Returns:** Detection result with threat flag, confidence, and method

### `detect_anomaly(data: dict) -> dict`

Perform anomaly detection using ML.

### `signature_match(event: dict) -> dict`

Match event against threat signatures.

## License

MIT License
