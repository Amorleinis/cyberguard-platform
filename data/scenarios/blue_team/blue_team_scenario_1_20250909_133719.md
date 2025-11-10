# Blue Team Exercise: Detect Execution through Command-Line Interface" Attacks

**Scenario Type:** Blue Team

**Detection Steps:**
- Monitor for indicators: master boot record; rootkit; persistence
- Monitor for indicators: USB drop; malware file; entice user
- Monitor for indicators: cmd.exe; powershell -nop -enc
- Monitor for indicators: delete files; shred command
- Monitor for indicators: imap/pop3 login attempts; password guess

**Metadata:** {
  "ID": "B-47827",
  "Type": "Blue Team",
  "Date": "2025-09-09T13:37:19.986916",
  "SeverityScore": 13,
  "Complexity": 5
}