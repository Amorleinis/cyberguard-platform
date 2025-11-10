# Purple Team Exercise: Simulate & Detect MITM: HTTPS Spoofing

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: SQL Injection: Error-based and monitor indicators: error response; stack trace
- Simulate attack: MITM: HTTPS Spoofing and monitor indicators: certificate replacement; proxy
- Simulate attack: Phishing: Malicious URL Shortener and monitor indicators: URL redirect; credential capture
- Simulate attack: Exploit Public-Facing Application: SQLi and monitor indicators: union select; drop table; blind injection
- Simulate attack: Category and monitor indicators: Keywords

**Metadata:** {
  "ID": "P-57947",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:37:16.744444",
  "SeverityScore": 9,
  "Complexity": 5
}