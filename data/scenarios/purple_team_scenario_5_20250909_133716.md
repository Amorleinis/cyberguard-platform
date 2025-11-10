# Purple Team Exercise: Simulate & Detect Brute Force: RDP Spray Variant 3

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: Persistence: WMI Subscription" and monitor indicators: wmic event; permanent script
- Simulate attack: APT: Multi-Stage Web Attack 2 and monitor indicators: custom scripts; exfiltration
- Simulate attack: Brute Force: RDP Spray Variant 3 and monitor indicators: RDP login attempts; password guessing
- Simulate attack: APT: Credential Theft Campaign 3 and monitor indicators: password dump; token reuse
- Simulate attack: Remote File Copy" and monitor indicators: scp; smb; ftp upload

**Metadata:** {
  "ID": "P-34179",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:37:16.638670",
  "SeverityScore": 4,
  "Complexity": 5
}