# Blue Team Exercise: Detect Emerging Malware: Reflective DLL Injection Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: dll injection; process hollowing
- Monitor for indicators: system(); exec(); shell command
- Monitor for indicators: memory-only execution; PowerShell
- Monitor for indicators: time-based blind SQLi; slow response extraction
- Monitor for indicators: fileless malware; persistence

**Metadata:** {
  "ID": "B-82568",
  "Type": "Blue Team",
  "Date": "2025-09-09T13:12:26.211809",
  "SeverityScore": 6,
  "Complexity": 5
}