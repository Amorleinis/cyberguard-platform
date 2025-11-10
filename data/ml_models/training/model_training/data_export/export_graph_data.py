"""
Export nodes and relationships from Neo4j to CSV for GNN training and analysis.
"""
import os
from neo4j import GraphDatabase
import pandas as pd

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Export nodes
def export_nodes(label, filename):
    with driver.session() as session:
        result = session.run(f"MATCH (n:{label}) RETURN n")
        data = [r['n'] for r in result]
        df = pd.DataFrame([dict(node) for node in data])
        df.to_csv(filename, index=False)
        print(f"Exported {len(df)} {label} nodes to {filename}")

# Export relationships
def export_relationships(type_, filename):
    with driver.session() as session:
        result = session.run(f"MATCH (a)-[r:{type_}]->(b) RETURN a, b")
        data = [(dict(r['a']), dict(r['b'])) for r in result]
        df = pd.DataFrame(data, columns=['source', 'target'])
        df.to_csv(filename, index=False)
        print(f"Exported {len(df)} {type_} relationships to {filename}")

if __name__ == '__main__':
    export_nodes('Asset', 'assets.csv')
    export_nodes('Threat', 'threats.csv')
    export_nodes('Technique', 'techniques.csv')
    export_nodes('Vulnerability', 'vulnerabilities.csv')
    export_relationships('HAS_VULNERABILITY', 'has_vulnerability.csv')
    export_relationships('USES', 'uses.csv')
    export_relationships('EXPLOITS', 'exploits.csv')
