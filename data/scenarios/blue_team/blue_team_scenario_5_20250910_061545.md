# Blue Team Exercise: Detect Cloud: Overprivileged IAM Role Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: intercepts TLS; session hijack
- Monitor for indicators: excessive permissions; role abuse
- Monitor for indicators: heap overflow; root escalation
- Monitor for indicators: aws-cli list; gcloud list; azure list
- Monitor for indicators: scp; smb copy; powershell remoting

**Metadata:** {
  "ID": "B-66906",
  "Type": "Blue Team",
  "Date": "2025-09-10T06:15:45.940192",
  "SeverityScore": 7,
  "Complexity": 5
}