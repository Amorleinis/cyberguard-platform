"""
Train a GNN model for intrusion prevention/detection using Neo4j Graph Data Science (GDS).
This script connects to Neo4j, projects the graph, runs node2vec for embeddings, and trains a classifier.
"""
import os
import logging
import threading
import sys
import time
from neo4j import GraphDatabase

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')

# Setup logging
logging.basicConfig(
    filename='gnn_training.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
)

def progress_bar(msg, stop_event, est_seconds=120):
    bar_stages = [
        '|...          ',
        '||....        ',
        '|||.......    ',
        '||||....      ',
        '|||||.......  ',
        '||||||....    ',
        '|||||||.....  ',
        '||||||||....  ',
        '|||||||||...  ',
        '||||||||||..  ',
        '|||||||||||.  ',
        '||||||||||||  '
    ]
    idx = 0
    sys.stdout.write(msg)
    sys.stdout.flush()
    start = time.time()
    while not stop_event.is_set():
        stage = bar_stages[idx % len(bar_stages)]
        sys.stdout.write(f'\r{msg}{stage}')
        sys.stdout.flush()
        time.sleep(est_seconds / (len(bar_stages) * 10))
        idx += 1
    sys.stdout.write(f'\r{msg}|||||||||||| Done\n')
    sys.stdout.flush()

# Connect to Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def run_gds_pipeline():
    try:
        with driver.session() as session:
            checkpoint_file = 'gnn_node2vec_checkpoint.flag'
            if os.path.exists(checkpoint_file):
                logging.info('Checkpoint found. Skipping node2vec embedding step.')
                print('Checkpoint found. Skipping node2vec embedding step.')
            else:
                logging.info('Projecting graph...')
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
                logging.info('Running node2vec...')
                print('Running node2vec...')
                stop_event = threading.Event()
                bar_thread = threading.Thread(target=progress_bar, args=("Node2vec in progress... ", stop_event, 120))
                bar_thread.start()
                try:
                    session.run('''
                        CALL gds.beta.node2vec.write(
                            'spectra_graph',
                            {
                                embeddingDimension: 64,
                                writeProperty: 'embedding'
                            }
                        )
                    ''')
                finally:
                    stop_event.set()
                    bar_thread.join()
                logging.info('Node2vec embeddings written to Neo4j node property "embedding".')
                print('Node2vec embeddings written to Neo4j node property "embedding".')
                print('You can now export embeddings and train a downstream classifier.')
                # Save checkpoint
                with open(checkpoint_file, 'w') as f:
                    f.write('node2vec complete')
                logging.info(f'Checkpoint file {checkpoint_file} written.')
            # Drop the projected graph
            session.run("CALL gds.graph.drop('spectra_graph') YIELD graphName;")
            logging.info('Graph dropped.')
            print('Graph dropped.')
    except Exception as e:
        logging.error(f"Error during GNN training: {e}")
        print(f"Error during GNN training: {e}")

if __name__ == '__main__':
    run_gds_pipeline()
