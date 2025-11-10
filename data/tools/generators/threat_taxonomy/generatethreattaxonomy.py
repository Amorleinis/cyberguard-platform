import csv
import random
from datetime import datetime

# Threat categories and example details
threat_categories = [
    {
        "Category": "Ransomware",
        "Keywords": ["ransom note", ".locked", "encrypted files", "payment instructions"],
        "Ports": "",
        "Protocol": "",
        "ClassType": "trojan-activity",
        "MITRE_IDs": "T1486",
        "SeverityOptions": ["high", "critical"],
    },
    {
        "Category": "Phishing",
        "Keywords": ["urgent password reset", "verify your account", "click the link", "account suspended"],
        "Ports": "",
        "Protocol": "",
        "ClassType": "",
        "MITRE_IDs": "T1566",
        "SeverityOptions": ["medium", "high"],
    },
    {
        "Category": "Man-in-the-Middle",
        "Keywords": ["CN=", "unexpected certificate", "ssl stripping", "proxy detected"],
        "Ports": "443",
        "Protocol": "tcp",
        "ClassType": "tls-attack",
        "MITRE_IDs": "T1557",
        "SeverityOptions": ["high"],
    },
    {
        "Category": "DDoS",
        "Keywords": ["dns amplification", "traffic spike", "udp flood", "slow network"],
        "Ports": "53",
        "Protocol": "udp",
        "ClassType": "dos",
        "MITRE_IDs": "T1498",
        "SeverityOptions": ["high"],
    },
    {
        "Category": "SQL Injection",
        "Keywords": ["select ", "union select", "drop table", "or '1'='1'"],
        "Ports": "80",
        "Protocol": "tcp",
        "ClassType": "web-application-attack",
        "MITRE_IDs": "T1190",
        "SeverityOptions": ["high"],
    },
    {
        "Category": "Brute Force Attack",
        "Keywords": ["failed login", "multiple login attempts", "account lockout", "invalid password"],
        "Ports": "",
        "Protocol": "",
        "ClassType": "",
        "MITRE_IDs": "T1110",
        "SeverityOptions": ["medium"],
    },
    {
        "Category": "Supply Chain Attack",
        "Keywords": ["update failed", "unexpected checksum", "signed software modified", "unauthorized update"],
        "Ports": "",
        "Protocol": "",
        "ClassType": "",
        "MITRE_IDs": "T1195",
        "SeverityOptions": ["medium", "high"],
    },
    {
        "Category": "Zero Day Exploit",
        "Keywords": ["exploit payload", "unknown command", "heap spray", "shellcode detected"],
        "Ports": "80",
        "Protocol": "tcp",
        "ClassType": "attempted-admin",
        "MITRE_IDs": "T1203",
        "SeverityOptions": ["critical", "high"],
    },
    {
        "Category": "IoT Vulnerabilities",
        "Keywords": ["default password", "firmware outdated", "iot anomaly", "unusual device traffic"],
        "Ports": "80;443",
        "Protocol": "tcp",
        "ClassType": "iot-activity",
        "MITRE_IDs": "T1595",
        "SeverityOptions": ["medium"],
    },
]

# Helper to generate fake indicators from keywords
def generate_indicators(keywords):
    indicators = random.sample(keywords, min(5, len(keywords)))
    # Pad to 5 indicators
    while len(indicators) < 5:
        indicators.append("")
    return indicators

def random_date():
    return datetime.strptime(
        f"{random.randint(2023,2025)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "%Y-%m-%d"
    ).date().isoformat()

filename = "generated_cyber_threat_taxonomy.csv"
with open(filename, mode='w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow([
        "ID", "Name", "Category", "Description", "Indicator1", "Indicator2", "Indicator3", "Indicator4", "Indicator5",
        "Ports", "Protocol", "SID", "ClassType", "Severity", "Keyword", "Threshold", "TimeFrame", "Field", "Reference",
        "MITRE Technique IDs", "Date"
    ])

    sid_base = 1000000
    for i in range(1, 301):  # Generate 300 entries
        cat = random.choice(threat_categories)
        indicators = generate_indicators(cat["Keywords"])
        severity = random.choice(cat["SeverityOptions"])
        threshold = random.randint(3, 50) if severity in ["medium", "high"] else random.randint(1, 10)
        timeframe = random.choice([60, 300, 600, 1800, 3600])  # seconds
        field = random.choice(["src_ip", "dst_ip", "user", "sender", "software_name"])
        name = f"{cat['Category']} Threat Variant {i}"
        description = f"Detects variant {i} of {cat['Category'].lower()} attacks."
        keyword = cat["Category"].lower().replace(" ", "_")
        reference = f"https://attack.mitre.org/techniques/{cat['MITRE_IDs']}/"

        writer.writerow([
            f"{sid_base + i}",
            name,
            cat["Category"],
            description,
            indicators[0],
            indicators[1],
            indicators[2],
            indicators[3],
            indicators[4],
            cat["Ports"],
            cat["Protocol"],
            f"{sid_base + i}",
            cat["ClassType"],
            severity,
            keyword,
            threshold,
            timeframe,
            field,
            reference,
            cat["MITRE_IDs"],
            random_date()
        ])

print(f"Generated {filename} with 300 cyber threat taxonomy entries.")
