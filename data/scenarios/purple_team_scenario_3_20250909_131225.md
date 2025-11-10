# Purple Team Exercise: Simulate & Detect Lateral Movement: RDP"

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: Persistence: Startup Folder" and monitor indicators: startup script; shortcut
- Simulate attack: Brute Force: RDP Variant 2 and monitor indicators: remote desktop password guessing
- Simulate attack: Lateral Movement: SSH" and monitor indicators: ssh login; key reuse; brute force
- Simulate attack: Lateral Movement: RDP" and monitor indicators: mstsc; session hijack

**Metadata:** {
  "ID": "P-64207",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:12:26.112132",
  "SeverityScore": 8,
  "Complexity": 4
}