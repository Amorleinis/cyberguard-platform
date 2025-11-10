# Blue Team Exercise: Detect APT: Fileless Malware Variant 1 Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: memory-only execution; PowerShell
- Monitor for indicators: firmware tampering; unusual traffic
- Monitor for indicators: encrypted files; ransom note; .locked
- Monitor for indicators: select * from; union select; drop table

**Metadata:** {
  "ID": "B-23532",
  "Type": "Blue Team",
  "Date": "2025-09-10T06:15:45.948672",
  "SeverityScore": 7,
  "Complexity": 4
}