# Purple Team Exercise: Simulate & Detect PowerShell

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: MITM: SSL Strip Variant 7 and monitor indicators: HTTPS downgraded; data sniffing
- Simulate attack: Advanced Malware: Rootkit" and monitor indicators: kernel module; hidden process; persistence
- Simulate attack: Malware: Exploit Kit Variant 4 and monitor indicators: zero-day exploit; memory-only execution
- Simulate attack: PowerShell and monitor indicators: powershell -nop -enc; script execution
- Simulate attack: Zero-Day Exploit: Mobile OS and monitor indicators: android RCE; iOS sandbox escape

**Metadata:** {
  "ID": "P-18697",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:07:15.248150",
  "SeverityScore": 8,
  "Complexity": 5
}