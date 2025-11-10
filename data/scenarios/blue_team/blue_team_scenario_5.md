# Blue Team Exercise: Detect Credential Dumping: Cached Domain Creds" Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: password spray; failed login tracking
- Monitor for indicators: scp; smb; ftp upload
- Monitor for indicators: lsass memory dump; kerberos ticket

**Metadata:** {
  "ID": "B-88799",
  "Type": "Blue Team",
  "Date": "2025-09-09T13:07:15.123315",
  "SeverityScore": 4,
  "Complexity": 3
}