# Purple Team Exercise: Simulate & Detect Exfiltration Over Other Network Medium

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: SQL Injection: Classic Variant 1 and monitor indicators: union select; sensitive data exfil
- Simulate attack: Malware: Banking Trojan Variant 10 and monitor indicators: keylogging; session hijacking
- Simulate attack: MITM: SSL Strip Variant 1 and monitor indicators: downgrade HTTPS; credential sniff
- Simulate attack: Exfiltration Over Other Network Medium and monitor indicators: dns tunnel; icmp tunnel; covert channel

**Metadata:** {
  "ID": "P-46144",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:12:49.181173",
  "SeverityScore": 2,
  "Complexity": 4
}