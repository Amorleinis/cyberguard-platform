# Blue Team Exercise: Detect Reconnaissance: Network Sniffing" Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: schtasks; cron job
- Monitor for indicators: encrypted archive; http POST; ftp upload
- Monitor for indicators: k8s pod escape; privilege escalation
- Monitor for indicators: blind boolean; time delay
- Monitor for indicators: tcpdump; wireshark; packet capture

**Metadata:** {
  "ID": "B-52364",
  "Type": "Blue Team",
  "Date": "2025-09-09T13:07:15.087568",
  "SeverityScore": 10,
  "Complexity": 5
}