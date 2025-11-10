"""
Train a GNN model for intrusion prevention/detection using Neo4j Graph Data Science (GDS).
This script connects to Neo4j, projects the graph, runs node2vec for embeddings, and trains a classifier.
"""
import os
from neo4j import GraphDatabase

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run_gds_pipeline():
    with driver.session() as session:
        # 1. Project the graph
        print('Projecting graph...')
        session.run('''
            CALL gds.graph.project(
                'spectra_graph',
                ['Asset', 'Threat', 'Technique', 'Vulnerability'],
                {
                    HAS_VULNERABILITY: {},
                    USES: {},
                    EXPLOITS: {}
                }
            )
        ''')
        # 2. Run node2vec for embeddings
        print('Running node2vec...')
        session.run('''
            CALL gds.beta.node2vec.write(
                'spectra_graph',
                {
                    embeddingDimension: 64,
                    writeProperty: 'embedding'
                }
            )
        ''')
        # 3. (Optional) Train a classifier using the embeddings (can be done in Python or GDS)
        print('Node2vec embeddings written to Neo4j node property "embedding".')
        print('You can now export embeddings and train a downstream classifier.')
        # 4. Drop the projected graph
        session.run("CALL gds.graph.drop('spectra_graph') YIELD graphName;")
        print('Graph dropped.')

if __name__ == '__main__':
    run_gds_pipeline()
