import csv

input_file = r"C:\Users\allue\OneDrive\Desktop\CyberGuardDefender\data\nvd\merged_neo4j_query_table_data.csv"
output_file = r"C:\Users\allue\OneDrive\Desktop\CyberGuardDefender\data\nvd\merged_neo4j_query_table_data_fixed.csv"

# Mapping of possible header names to required names
with open(input_file, 'r', newline='', encoding='utf-8') as fin, \
     open(output_file, 'w', newline='', encoding='utf-8') as fout:
    reader = csv.DictReader(fin)
    writer = csv.DictWriter(fout, fieldnames=['cve_id', 'technique'])
    writer.writeheader()
    for row in reader:
        new_row = {
            'cve_id': row.get('v.cve_id', '').strip(),
            'technique': row.get('tech.name', '').strip()
        }
        if new_row['cve_id'] and new_row['technique']:
            writer.writerow(new_row)
print(f"Fixed header and saved to {output_file}")
