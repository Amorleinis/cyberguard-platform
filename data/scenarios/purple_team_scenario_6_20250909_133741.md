# Purple Team Exercise: Simulate & Detect DDoS: SYN Flood Variant 1

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: SQL Injection: Classic Variant 1 and monitor indicators: union select; sensitive data exfil
- Simulate attack: DDoS: SYN Flood Variant 1 and monitor indicators: TCP connection exhaustion
- Simulate attack: Lateral Movement: Windows Admin Shares" and monitor indicators: \\C$; \\ADMIN$; smb copy
- Simulate attack: Lateral Movement: PsExec" and monitor indicators: psexec; admin share; remote cmd

**Metadata:** {
  "ID": "P-39694",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:37:41.415192",
  "SeverityScore": 6,
  "Complexity": 4
}