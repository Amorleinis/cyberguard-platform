"""
Export node2vec embeddings from Neo4j to CSV for downstream ML tasks.
"""
import os
import pandas as pd
from neo4j import GraphDatabase

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# Export all nodes with their embeddings
def export_embeddings(filename='node2vec_embeddings.csv'):
    with driver.session() as session:
        # Get all nodes with the 'embedding' property
        result = session.run('''
            MATCH (n) WHERE n.embedding IS NOT NULL
            RETURN id(n) AS node_id, labels(n) AS labels, n.embedding AS embedding
        ''')
        rows = []
        for record in result:
            node_id = record['node_id']
            labels = '|'.join(record['labels'])
            embedding = record['embedding']
            rows.append({'node_id': node_id, 'labels': labels, **{f'emb_{i}': v for i, v in enumerate(embedding)}})
        df = pd.DataFrame(rows)
        df.to_csv(filename, index=False)
        print(f'Exported {len(df)} node embeddings to {filename}')

if __name__ == '__main__':
    export_embeddings()
