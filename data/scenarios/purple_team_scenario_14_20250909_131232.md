# Purple Team Exercise: Simulate & Detect Lateral Movement: WinRM"

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: Reconnaissance: Permission Groups Discovery" and monitor indicators: net group; getent group
- Simulate attack: Brute Force: Web Login and monitor indicators: form submit; login attempts
- Simulate attack: Lateral Movement: WinRM" and monitor indicators: winrm; powershell remoting
- Simulate attack: Brute Force: SSH Spray Variant 3 and monitor indicators: credential spray; failed login
- Simulate attack: SQL Injection: Error-based and monitor indicators: error response; stack trace

**Metadata:** {
  "ID": "P-15997",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:12:46.173304",
  "SeverityScore": 9,
  "Complexity": 5
}