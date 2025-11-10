# Purple Team Exercise: Simulate & Detect Bootkit

**Scenario Type:** Purple Team

**Simulation & Detection Steps:**
- Simulate attack: Brute Force: SSH Credential Spray Variant 5 and monitor indicators: password spray; failed login tracking
- Simulate attack: Bootkit and monitor indicators: master boot record; rootkit; persistence
- Simulate attack: Cloud: S3 Bucket Exposure Variant 9 and monitor indicators: public bucket; data leak
- Simulate attack: Impair Defenses: Timestomp and monitor indicators: file timestomping; metadata change
- Simulate attack: IoT: Smart Lock Exploit 3 and monitor indicators: default creds; remote unlock

**Metadata:** {
  "ID": "P-58565",
  "Type": "Purple Team",
  "Date": "2025-09-09T13:12:46.098787",
  "SeverityScore": 6,
  "Complexity": 5
}