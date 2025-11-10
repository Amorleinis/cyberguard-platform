# Purple Team Exercise: Simulate & Detect Ransomware: CryptoLocker Variant

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: DDoS: HTTP Flood and monitor indicators: GET request storm; botnet
- Simulate attack: Ransomware: CryptoLocker Variant and monitor indicators: encrypted files; ransom note; .locked
- Simulate attack: SQL Injection: Error-Based Variant 6 and monitor indicators: stack trace info leak; sensitive data
- Simulate attack: Brute Force: Email and monitor indicators: imap/pop3 login attempts; password guess
- Simulate attack: Command and Control over DNS" and monitor indicators: dns tunnel; txt record; beacon

**Metadata:** {
  "ID": "P-85252",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:12:26.223371",
  "SeverityScore": 11,
  "Complexity": 5
}