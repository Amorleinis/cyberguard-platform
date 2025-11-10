# Blue Team Exercise: Detect DDoS: SYN Flood Variant 1 Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: union select; sensitive data exfil
- Monitor for indicators: TCP connection exhaustion
- Monitor for indicators: \\C$; \\ADMIN$; smb copy
- Monitor for indicators: psexec; admin share; remote cmd

**Metadata:** {
  "ID": "B-64159",
  "Type": "Blue Team",
  "Date": "2025-09-09T13:37:41.412232",
  "SeverityScore": 6,
  "Complexity": 4
}