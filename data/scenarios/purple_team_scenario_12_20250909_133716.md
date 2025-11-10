# Purple Team Exercise: Simulate & Detect Cloud: Overprivileged IAM Role

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: Defense Evasion: Masquerading" and monitor indicators: rename process; fake service
- Simulate attack: Persistence: WMI Subscription" and monitor indicators: wmic event; permanent script
- Simulate attack: Cloud: Overprivileged IAM Role and monitor indicators: excessive permissions; role abuse
- Simulate attack: APT: Fileless Malware Variant 12 and monitor indicators: WMI persistence; obfuscated scripts
- Simulate attack: MITM: Rogue Proxy Variant 7 and monitor indicators: intercepts HTTPS; session hijack

**Metadata:** {
  "ID": "P-86472",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:37:16.695487",
  "SeverityScore": 7,
  "Complexity": 5
}