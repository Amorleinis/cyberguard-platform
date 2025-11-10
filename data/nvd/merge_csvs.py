import csv

# List of CSV files to merge
csv_files = [
    r"C:\Users\allue\OneDrive\Desktop\CyberGuardDefender\data\nvd\neo4j_query_table_data_2025-8-11.csv",
    r"C:\Users\allue\OneDrive\Desktop\CyberGuardDefender\data\nvd\neo4j_query_table_data1_2025-8-11.csv",
    r"C:\Users\allue\OneDrive\Desktop\CyberGuardDefender\data\nvd\neo4j_query_table_data2_2025-8-11.csv"
]

output_file = r"C:\Users\allue\OneDrive\Desktop\CyberGuardDefender\data\nvd\merged_neo4j_query_table_data.csv"

header_saved = False
with open(output_file, 'w', newline='', encoding='utf-8') as fout:
    writer = None
    for file in csv_files:
        with open(file, 'r', newline='', encoding='utf-8') as fin:
            reader = csv.reader(fin)
            header = next(reader)
            if not header_saved:
                writer = csv.writer(fout)
                writer.writerow(header)
                header_saved = True
            for row in reader:
                writer.writerow(row)
print(f"Merged {len(csv_files)} files into {output_file}")
