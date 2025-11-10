# Blue Team Exercise: Detect Exploitation for Privilege Escalation: MacOS" Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: service install; sc.exe
- Monitor for indicators: exploit kernel; root access
- Monitor for indicators: alters traffic payload; data leak
- Monitor for indicators: delete files; shred command; disk wipe

**Metadata:** {
  "ID": "B-40787",
  "Type": "Blue Team",
  "Date": "2025-09-10T06:15:45.956693",
  "SeverityScore": 10,
  "Complexity": 4
}