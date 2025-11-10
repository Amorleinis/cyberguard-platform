# Blue Team Exercise: Detect Disabling Security Tools" Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: NTLM hash reuse; Mimikatz
- Monitor for indicators: password spray; account lockout
- Monitor for indicators: AV stop; firewall off; SIEM disable
- Monitor for indicators: kernel exploit; root privilege

**Metadata:** {
  "ID": "B-26233",
  "Type": "Blue Team",
  "Date": "2025-09-10T06:15:45.898456",
  "SeverityScore": 12,
  "Complexity": 4
}