# Blue Team Exercise: Detect MITM: SSL Strip Variant 7 Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: HTTPS downgraded; data sniffing
- Monitor for indicators: kernel module; hidden process; persistence
- Monitor for indicators: zero-day exploit; memory-only execution
- Monitor for indicators: powershell -nop -enc; script execution
- Monitor for indicators: android RCE; iOS sandbox escape

**Metadata:** {
  "ID": "B-56759",
  "Type": "Blue Team",
  "Date": "2025-09-09T13:07:15.246750",
  "SeverityScore": 8,
  "Complexity": 5
}