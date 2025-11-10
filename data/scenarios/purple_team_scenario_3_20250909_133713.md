# Purple Team Exercise: Simulate & Detect Credential Dumping: SAM"

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: Credential Dumping: SAM" and monitor indicators: reg query SAM; offline extraction
- Simulate attack: SQL Injection: Error-based and monitor indicators: error response; stack trace
- Simulate attack: SQL Injection: Time-based and monitor indicators: time delay; conditional query
- Simulate attack: Brute Force: RDP Variant 2 and monitor indicators: remote desktop password guessing
- Simulate attack: Spearphishing Link and monitor indicators: redirect; shortened url; credential harvest

**Metadata:** {
  "ID": "P-58996",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:37:13.614157",
  "SeverityScore": 11,
  "Complexity": 5
}