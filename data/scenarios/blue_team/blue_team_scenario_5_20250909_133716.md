# Blue Team Exercise: Detect Persistence: WMI Subscription" Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: wmic event; permanent script
- Monitor for indicators: custom scripts; exfiltration
- Monitor for indicators: RDP login attempts; password guessing
- Monitor for indicators: password dump; token reuse
- Monitor for indicators: scp; smb; ftp upload

**Metadata:** {
  "ID": "B-20057",
  "Type": "Blue Team",
  "Date": "2025-09-09T13:37:16.635777",
  "SeverityScore": 4,
  "Complexity": 5
}