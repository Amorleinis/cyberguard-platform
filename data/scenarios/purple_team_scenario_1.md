# Purple Team Exercise: Simulate & Detect Reconnaissance: Network Sniffing"

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: Persistence: Scheduled Task" and monitor indicators: schtasks; cron job
- Simulate attack: Exfiltration Over C2 Channel and monitor indicators: encrypted archive; http POST; ftp upload
- Simulate attack: Cloud: Container Breakout Variant 2 and monitor indicators: k8s pod escape; privilege escalation
- Simulate attack: SQL Injection: Blind and monitor indicators: blind boolean; time delay
- Simulate attack: Reconnaissance: Network Sniffing" and monitor indicators: tcpdump; wireshark; packet capture

**Metadata:** {
  "ID": "P-25438",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:07:15.092103",
  "SeverityScore": 10,
  "Complexity": 5
}