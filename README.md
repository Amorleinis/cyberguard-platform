# CyberGuard Industries - Threat Intelligence Platform

**Author:** Lance A. Brady & AI Collaboration  
**License:** Apache 2.0  
**Status:** Production Ready

---

## 🚀 Published Packages

All 7 security engine packages are available on GitHub:

### Individual Engines

| Engine | Repository | Install Command |
|--------|-----------|----------------|
| **Intelligence** | [threat-intelligence-engine](https://github.com/Amorleinis/threat-intelligence-engine) | `pip install git+https://github.com/Amorleinis/threat-intelligence-engine` |
| **Prevention** | [threat-prevention-engine](https://github.com/Amorleinis/threat-prevention-engine) | `pip install git+https://github.com/Amorleinis/threat-prevention-engine` |
| **Detection** | [threat-detection-engine](https://github.com/Amorleinis/threat-detection-engine) | `pip install git+https://github.com/Amorleinis/threat-detection-engine` |
| **Response** | [incident-response-engine](https://github.com/Amorleinis/incident-response-engine) | `pip install git+https://github.com/Amorleinis/incident-response-engine` |
| **Isolation** | [threat-isolation-engine](https://github.com/Amorleinis/threat-isolation-engine) | `pip install git+https://github.com/Amorleinis/threat-isolation-engine` |
| **Mitigation** | [threat-mitigation-engine](https://github.com/Amorleinis/threat-mitigation-engine) | `pip install git+https://github.com/Amorleinis/threat-mitigation-engine` |
| **Recovery** | [system-recovery-engine](https://github.com/Amorleinis/system-recovery-engine) | `pip install git+https://github.com/Amorleinis/system-recovery-engine` |

---

## 📁 Directory Structure

```
datasets/
├── intelligence/          # Intelligence Engine package
├── prevention/           # Prevention Engine package
├── detection/            # Detection Engine package
├── response/             # Response Engine package
├── isolation/            # Isolation Engine package
├── mitigation/           # Mitigation Engine package
├── recovery/             # Recovery Engine package
├── docs/                 # All documentation
├── scripts/              # Installation & setup scripts
├── demos/                # Demo files and examples
├── tests/                # Test files and results
├── data/                 # Real CVE and threat data
├── requirements.txt      # Unified platform dependencies
└── setup.py              # Unified platform setup
```

---

## 🎯 Quick Start

### Install Individual Engine
```bash
pip install git+https://github.com/Amorleinis/threat-intelligence-engine
```

### Use in Your Code
```python
from threat_intelligence_engine import ThreatIntelligenceEngine

engine = ThreatIntelligenceEngine(db_path="intel.db")
analysis = engine.analyze_cve(cve_data)
```

### Run the full platform locally
- Use Python 3.11 and create a venv: `py -3.11 -m venv .venv`
- Activate it: `\.\.venv\Scripts\Activate.ps1`
- Copy `.env.example` to `.env` and set `SECRET_KEY`, `DATABASE_URL` (default SQLite, Postgres: `postgresql+psycopg2://cyberguard:cyberguard@db:5432/cyberguard`), and `CORS_ALLOW_ORIGINS`
- Install backend deps: `pip install -r backend\requirements.txt`
- Launch everything: `./start-platform.ps1` (backend at http://127.0.0.1:8000, web at http://localhost:3000)
- Or run backend + Postgres with Docker Compose: `docker compose -f docker-compose.backend.yml up --build` (runs Alembic migrations automatically)

### Prepare admin and database
- Set `DATABASE_URL` in `.env` (SQLite default; Postgres recommended)
- Seed admin user (local venv): `cd backend\scripts; ..\..\.venv\Scripts\python seed_admin.py`
- Seed admin inside compose: `docker compose -f docker-compose.backend.yml exec backend python scripts/seed_admin.py`

---

## 📚 Documentation

- **[Installation Guide](docs/INSTALLATION.md)** - Detailed installation instructions
- **[Quick Start](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[Plug & Play Guide](docs/PLUG_AND_PLAY_README.md)** - Zero-config demos
- **[Package Portability](docs/PACKAGE_PORTABILITY.md)** - Standalone usage
- **[Next Steps](docs/NEXT_STEPS.md)** - Publishing and distribution

---

## 🛠️ Scripts

All scripts are in the `scripts/` folder:

- `install_unified.ps1` - Install complete platform
- `install_individual.ps1` - Install individual engines
- `LAUNCH_PLUG_AND_PLAY.ps1` - Run plug-and-play demos
- `UPDATE_LICENSES.ps1` - Update all licenses
- `UPLOAD_TO_GITHUB.ps1` - GitHub publishing script

---

## 🎮 Demos

All demos are in the `demos/` folder:

- `demo_intelligence_plug_and_play.py` - CVE analysis demo
- `demo_detection_plug_and_play.py` - Threat detection demo
- `PLUG_AND_PLAY_DEMO.py` - Complete platform demo
- `example_individual_engines.py` - Individual engine examples
- `example_unified_bundle.py` - Unified platform example

---

## 🧪 Tests

Run tests:
```bash
cd tests
python run_all_tests.py
```

---

## 📊 Features

✅ **7 Production-Ready Security Engines**  
✅ **Apache 2.0 Open Source License**  
✅ **Plug-and-Play Demos with Real Data**  
✅ **Complete API Documentation**  
✅ **Professional Branding**  
✅ **GitHub Published**  
✅ **Portable & Self-Contained**

---

## 🤝 Contributing

We welcome contributions! Please see individual repositories for contribution guidelines.

---

## 📄 License

Apache License 2.0 - See [LICENSE](intelligence/LICENSE) for details

**Copyright 2025 CyberGuard Industries**  
**Original Author: Lance Brady with AI Collaboration**

---

## 📧 Contact

For questions or support, visit the individual GitHub repositories and open an issue.

---

**Built with ❤️ by CyberGuard Industries**
