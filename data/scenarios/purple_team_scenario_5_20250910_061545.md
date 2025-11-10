# Purple Team Exercise: Simulate & Detect Cloud: Overprivileged IAM Role

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: MITM: SSL Strip Variant 2 and monitor indicators: intercepts TLS; session hijack
- Simulate attack: Cloud: Overprivileged IAM Role and monitor indicators: excessive permissions; role abuse
- Simulate attack: Zero-Day: Windows Kernel Variant 12 and monitor indicators: heap overflow; root escalation
- Simulate attack: Reconnaissance: Cloud Service Discovery" and monitor indicators: aws-cli list; gcloud list; azure list
- Simulate attack: Lateral Tool Transfer and monitor indicators: scp; smb copy; powershell remoting

**Metadata:** {
  "ID": "P-96222",
  "Type": "Purple Team",
  "Date": "2025-09-10T06:15:45.942543",
  "SeverityScore": 7,
  "Complexity": 5
}