# Purple Team Exercise: Simulate & Detect Cloud: Container Breakout Variant 2

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: Scripting: PowerShell" and monitor indicators: powershell -nop -enc; invoke-expression
- Simulate attack: Impact: Disk Wipe" and monitor indicators: diskpart; sdelete; wipe all
- Simulate attack: MITM: Rogue WiFi Variant 14 and monitor indicators: traffic modification; data exfiltration
- Simulate attack: Cloud: Container Breakout Variant 2 and monitor indicators: k8s pod escape; privilege escalation

**Metadata:** {
  "ID": "P-63314",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:37:20.231767",
  "SeverityScore": 5,
  "Complexity": 4
}