# Blue Team Exercise: Detect Cloud: Container Breakout Variant 3 Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: bash script; pipe; shell
- Monitor for indicators: union select; sensitive data exfil
- Monitor for indicators: winrm; powershell remoting; wmi execute
- Monitor for indicators: docker escape; host root access
- Monitor for indicators: environment variable; code repo leak

**Metadata:** {
  "ID": "B-56523",
  "Type": "Blue Team",
  "Date": "2025-09-10T06:15:45.964765",
  "SeverityScore": 7,
  "Complexity": 5
}