"""
Advanced Folder Organization Script
Consolidates DATAX, neo4j, neo4j_data, and NVD into unified data/ structure
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AdvancedOrganizer:
    """Organizes multiple scattered folders into unified structure"""
    
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.data_root = self.workspace_root / "data"
        self.stats = {
            'moved': 0,
            'errors': 0,
            'skipped': 0,
            'by_category': {}
        }
        
    def create_unified_structure(self):
        """Create comprehensive unified data structure"""
        
        structure = {
            # Machine Learning & AI Models
            'ml_models': [
                'training',
                'checkpoints',
                'embeddings',
                'clustering',
                'experiments'
            ],
            
            # Neo4j Database
            'neo4j': [
                'nodes',
                'relationships', 
                'graph_data',
                'imports',
                'scripts',
                'database_files'
            ],
            
            # NVD Data (already exists from previous org)
            'nvd': [
                'feeds',
                'processed',
                'further'
            ],
            
            # Training Data & Datasets
            'datasets': [
                'raw',
                'processed',
                'features',
                'taxonomy',
                'exports'
            ],
            
            # Visualization & Analytics
            'visualizations': [
                'plots',
                'dashboards',
                'reports'
            ],
            
            # Configuration & Utils
            'config': [
                'experiments',
                'pipelines'
            ],
            
            # Scripts & Tools
            'tools': [
                'data_loaders',
                'utilities',
                'generators'
            ],
            
            # Legacy/Archive (for old DATAX structure)
            'archive': [
                'datax_original',
                'neo4j_legacy'
            ]
        }
        
        logger.info("📁 Creating unified data structure...")
        for category, subdirs in structure.items():
            cat_path = self.data_root / category
            cat_path.mkdir(parents=True, exist_ok=True)
            
            for subdir in subdirs:
                (cat_path / subdir).mkdir(exist_ok=True)
                
        logger.info(f"✅ Created {len(structure)} main categories")
        
    def organize_datax(self):
        """Organize DATAX folder contents"""
        logger.info("\n🤖 Organizing DATAX folder...")
        
        datax_path = self.workspace_root / "DATAX"
        if not datax_path.exists():
            logger.warning("DATAX folder not found")
            return
            
        # ML Training Scripts
        training_scripts = [
            'train_model.py',
            'train_hybrid_model.py', 
            'train_full_hybrid_model.py',
            'data_loader.py',
            'spectra_blocks.py',
            'hybrid_neuro_symbolic_framework_agnostic_scaffold_code_python.py',
            'hybrid_neuro_symbolic_gnn_gnn_rbm_transformer_rbf_lstm_py_torch_scaffold.py',
            'model_logic_8_rules_integrated_code_python.py'
        ]
        
        for script in training_scripts:
            src = datax_path / script
            if src.exists():
                dest = self.data_root / "ml_models" / "training" / script
                self._move_file(src, dest, 'ml_models')
                
        # Figures/Visualizations
        for i in range(1, 4):
            fig = datax_path / f"Figure_{i}.png"
            if fig.exists():
                dest = self.data_root / "visualizations" / "plots" / f"Figure_{i}.png"
                self._move_file(fig, dest, 'visualizations')
                
        # DATAX data subfolder
        datax_data = datax_path / "data"
        if datax_data.exists():
            self._organize_datax_data(datax_data)
            
        # Model training subfolder
        model_training = datax_path / "model_training"
        if model_training.exists():
            dest = self.data_root / "ml_models" / "training" / "model_training"
            self._move_folder(model_training, dest, 'ml_models')
            
        # Spectra projects (CyberGuardDefender, spectra_guardian, etc.)
        spectra_folders = ['CyberGuardDefender', 'spectra_guardian', 'spectra_phoenix', 'spectra_sentry', 'DataComverged']
        for folder in spectra_folders:
            src = datax_path / folder
            if src.exists():
                dest = self.data_root / "archive" / "datax_original" / folder
                self._move_folder(src, dest, 'archive')
                
        # README
        readme = datax_path / "README.md"
        if readme.exists():
            dest = self.data_root / "ml_models" / "README.md"
            self._move_file(readme, dest, 'ml_models')
            
    def _organize_datax_data(self, datax_data_path):
        """Organize DATAX/data subfolder contents"""
        logger.info("  📊 Processing DATAX/data contents...")
        
        # NVD JSON files
        nvd_files = list(datax_data_path.glob("nvdcve-*.json"))
        for nvd_file in nvd_files:
            dest = self.data_root / "nvd" / "feeds" / nvd_file.name
            self._move_file(nvd_file, dest, 'nvd')
            
        # CSV datasets
        csv_mappings = {
            'assets.csv': 'datasets/raw',
            'assets_features.csv': 'datasets/features',
            'uses.csv': 'datasets/raw',
            'cybersecurity_threat_taxonomy_full.csv': 'datasets/taxonomy',
            'cluster_centroids.csv': 'ml_models/clustering',
            'cluster_label_summary.csv': 'ml_models/clustering',
            'cluster_sizes.html': 'visualizations/dashboards',
            'cluster_transition_matrix.csv': 'ml_models/clustering',
            'label_cluster_confusion_matrix.csv': 'ml_models/clustering',
            'label_distribution_per_cluster.html': 'visualizations/dashboards',
            'node2vec_embeddings.csv': 'ml_models/embeddings',
            'node2vec_embeddings_with_clusters.csv': 'ml_models/embeddings',
            'node2vec_embeddings_with_clusters_and_outliers.csv': 'ml_models/embeddings',
            'silhouette_per_cluster.csv': 'ml_models/clustering',
            'tsne_by_cluster_checkpoint.csv': 'ml_models/checkpoints',
            'tsne_by_label_checkpoint.csv': 'ml_models/checkpoints'
        }
        
        for filename, dest_path in csv_mappings.items():
            src = datax_data_path / filename
            if src.exists():
                dest = self.data_root / dest_path / filename
                category = dest_path.split('/')[0]
                self._move_file(src, dest, category)
                
        # Python scripts
        scripts = ['cluster_lookup.py', 'run_training_pipeline.py', 'utils.py']
        for script in scripts:
            src = datax_data_path / script
            if src.exists():
                dest = self.data_root / "tools" / "utilities" / script
                self._move_file(src, dest, 'tools')
                
        # Config files
        config = datax_data_path / "experiment_config.yaml"
        if config.exists():
            dest = self.data_root / "config" / "experiments" / "experiment_config.yaml"
            self._move_file(config, dest, 'config')
            
        # Subfolders
        subfolders = {
            'exports': 'datasets/exports',
            'processed': 'datasets/processed',
            'raw': 'datasets/raw',
            'nvd': 'nvd/processed',
            'generate_threat_taxonomy': 'tools/generators/threat_taxonomy'
        }
        
        for folder, dest_path in subfolders.items():
            src = datax_data_path / folder
            if src.exists():
                dest = self.data_root / dest_path
                category = dest_path.split('/')[0]
                self._move_folder(src, dest, category)
                
    def organize_neo4j(self):
        """Organize neo4j folder contents"""
        logger.info("\n🔷 Organizing neo4j folder...")
        
        neo4j_path = self.workspace_root / "neo4j"
        if not neo4j_path.exists():
            logger.warning("neo4j folder not found")
            return
            
        # Scripts
        scripts = [
            'add_id_columns.py',
            'get_import_dir.py',
            'ingest_csvs.py',
            'ingest_via_driver.py',
            'monitor_ingest.py'
        ]
        
        for script in scripts:
            src = neo4j_path / script
            if src.exists():
                dest = self.data_root / "neo4j" / "scripts" / script
                self._move_file(src, dest, 'neo4j')
                
        # Cypher files
        cypher_files = ['import_relationships.cypher', 'init.cypher']
        for cypher in cypher_files:
            src = neo4j_path / cypher
            if src.exists():
                dest = self.data_root / "neo4j" / "scripts" / cypher
                self._move_file(src, dest, 'neo4j')
                
        # Requirements
        req = neo4j_path / "requirements.txt"
        if req.exists():
            dest = self.data_root / "neo4j" / "requirements.txt"
            self._move_file(req, dest, 'neo4j')
            
        # Nodes folder
        nodes = neo4j_path / "nodes"
        if nodes.exists():
            dest = self.data_root / "neo4j" / "nodes"
            self._move_folder(nodes, dest, 'neo4j')
            
        # Graph folder
        graph = neo4j_path / "graph"
        if graph.exists():
            dest = self.data_root / "neo4j" / "graph_data"
            self._move_folder(graph, dest, 'neo4j')
            
    def organize_neo4j_data(self):
        """Organize neo4j_data folder (database files)"""
        logger.info("\n💾 Organizing neo4j_data folder...")
        
        neo4j_data_path = self.workspace_root / "neo4j_data"
        if not neo4j_data_path.exists():
            logger.warning("neo4j_data folder not found")
            return
            
        # Move entire database folder
        dest = self.data_root / "neo4j" / "database_files"
        self._move_folder(neo4j_data_path, dest, 'neo4j')
        
    def organize_nvd(self):
        """Organize NVD folder (currently empty)"""
        logger.info("\n📋 Checking NVD folder...")
        
        nvd_path = self.workspace_root / "NVD"
        if not nvd_path.exists():
            logger.warning("NVD folder not found")
            return
            
        # Check if empty
        if not any(nvd_path.iterdir()):
            logger.info("  NVD folder is empty, removing...")
            try:
                nvd_path.rmdir()
                logger.info("  ✅ Removed empty NVD folder")
            except Exception as e:
                logger.warning(f"  ⚠️  Could not remove NVD folder: {e}")
        else:
            # Move any contents to data/nvd
            for item in nvd_path.iterdir():
                dest = self.data_root / "nvd" / "further" / item.name
                if item.is_dir():
                    self._move_folder(item, dest, 'nvd')
                else:
                    self._move_file(item, dest, 'nvd')
                    
    def _move_file(self, src, dest, category):
        """Move a file with error handling"""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Skip if destination already exists
            if dest.exists():
                logger.info(f"  ⏭️  Skipped (exists): {src.name}")
                self.stats['skipped'] += 1
                return
                
            shutil.move(str(src), str(dest))
            logger.info(f"  ✓ {src.name} → {category}/{dest.relative_to(self.data_root / category)}")
            
            self.stats['moved'] += 1
            self.stats['by_category'][category] = self.stats['by_category'].get(category, 0) + 1
            
        except Exception as e:
            logger.error(f"  ✗ Error moving {src.name}: {e}")
            self.stats['errors'] += 1
            
    def _move_folder(self, src, dest, category):
        """Move a folder with error handling"""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            # Skip if destination already exists
            if dest.exists():
                logger.info(f"  ⏭️  Skipped folder (exists): {src.name}")
                self.stats['skipped'] += 1
                return
                
            shutil.move(str(src), str(dest))
            logger.info(f"  ✓ {src.name}/ → {category}/{dest.relative_to(self.data_root / category)}/")
            
            self.stats['moved'] += 1
            self.stats['by_category'][category] = self.stats['by_category'].get(category, 0) + 1
            
        except Exception as e:
            logger.error(f"  ✗ Error moving folder {src.name}: {e}")
            self.stats['errors'] += 1
            
    def cleanup_empty_folders(self):
        """Remove empty source folders"""
        logger.info("\n🧹 Cleaning up empty folders...")
        
        folders_to_check = ['DATAX', 'neo4j', 'neo4j_data', 'NVD']
        
        for folder_name in folders_to_check:
            folder_path = self.workspace_root / folder_name
            if folder_path.exists():
                try:
                    # Check if empty (including subfolders)
                    if not any(folder_path.rglob('*')):
                        folder_path.rmdir()
                        logger.info(f"  ✓ Removed empty folder: {folder_name}")
                    else:
                        # Try to remove if only has __pycache__ or empty subdirs
                        has_content = False
                        for item in folder_path.rglob('*'):
                            if item.is_file() and '__pycache__' not in str(item):
                                has_content = True
                                break
                        
                        if not has_content:
                            shutil.rmtree(folder_path)
                            logger.info(f"  ✓ Removed folder with only cache: {folder_name}")
                        else:
                            logger.info(f"  ⚠️  Folder still has content: {folder_name}")
                            
                except Exception as e:
                    logger.warning(f"  ⚠️  Could not remove {folder_name}: {e}")
                    
    def create_master_readme(self):
        """Create master README for unified data structure"""
        logger.info("\n📝 Creating master README...")
        
        readme_content = f"""# Unified Data Repository
**Organized on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This directory contains all workspace data organized into logical categories.

## Directory Structure

### 🤖 ml_models/
Machine Learning models, training scripts, and artifacts
- `training/` - Training scripts and pipelines
- `checkpoints/` - Model checkpoints and snapshots
- `embeddings/` - Node2Vec and other embeddings
- `clustering/` - Clustering results and metrics
- `experiments/` - Experimental model configurations

### 🔷 neo4j/
Neo4j graph database files and tools
- `nodes/` - Node CSV files for import
- `relationships/` - Relationship CSV files
- `graph_data/` - Graph exports and data
- `imports/` - Import scripts and configurations
- `scripts/` - Cypher queries and Python utilities
- `database_files/` - Neo4j database storage (databases/, dbms/, transactions/)

### 📋 nvd/
National Vulnerability Database (NVD) data
- `feeds/` - Raw NVD JSON feeds (2020-2024)
- `processed/` - Processed and analyzed NVD data
- `further/` - Additional NVD processing results

### 📊 datasets/
Training datasets and feature engineering
- `raw/` - Raw unprocessed datasets
- `processed/` - Cleaned and processed data
- `features/` - Feature-engineered datasets
- `taxonomy/` - Cybersecurity taxonomy files
- `exports/` - Dataset exports

### 📈 visualizations/
Charts, plots, and dashboards
- `plots/` - Static visualization images
- `dashboards/` - Interactive HTML dashboards
- `reports/` - Analysis reports

### ⚙️ config/
Configuration files
- `experiments/` - Experiment configurations (YAML)
- `pipelines/` - Pipeline configurations

### 🛠️ tools/
Utility scripts and data loaders
- `data_loaders/` - Data loading utilities
- `utilities/` - Helper scripts
- `generators/` - Data generation tools

### 📦 archive/
Legacy code and deprecated projects
- `datax_original/` - Original DATAX projects (CyberGuardDefender, Spectra)
- `neo4j_legacy/` - Old Neo4j configurations

## Previous Locations

This unified structure consolidates data from:
- `DATAX/` - ML models, training data, embeddings
- `neo4j/` - Graph database scripts and node data
- `neo4j_data/` - Neo4j database files
- `NVD/` - (was empty, removed)
- Individual scattered files across workspace

## Organization Statistics

**Total Items Organized:** {self.stats['moved']}
**Items per Category:**
"""
        
        for category in sorted(self.stats['by_category'].keys()):
            count = self.stats['by_category'][category]
            readme_content += f"- {category}: {count} items\n"
            
        readme_content += f"""
**Errors:** {self.stats['errors']}
**Skipped (already exist):** {self.stats['skipped']}

## Quick Access

- **Train Models:** `ml_models/training/`
- **View Data:** `datasets/`
- **Neo4j Setup:** `neo4j/scripts/`
- **Vulnerabilities:** `nvd/feeds/`
- **Analytics:** `visualizations/dashboards/`

---
*Auto-generated by Advanced Workspace Organizer*
"""
        
        readme_path = self.data_root / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
            
        logger.info(f"  ✓ Created {readme_path}")
        
    def print_summary(self):
        """Print organization summary"""
        logger.info("\n" + "="*80)
        logger.info("📊 ORGANIZATION SUMMARY")
        logger.info("="*80)
        logger.info(f"\n✅ Successfully moved: {self.stats['moved']} items")
        logger.info(f"⏭️  Skipped (existed): {self.stats['skipped']} items")
        logger.info(f"❌ Errors: {self.stats['errors']} items")
        
        if self.stats['by_category']:
            logger.info("\n📁 Items per category:")
            for category in sorted(self.stats['by_category'].keys()):
                count = self.stats['by_category'][category]
                logger.info(f"  • {category}: {count} items")
                
        logger.info("\n" + "="*80)
        
    def execute(self, dry_run=False):
        """Execute the full organization process"""
        if dry_run:
            logger.info("🔍 DRY RUN MODE - No files will be moved\n")
        else:
            logger.info("🚀 EXECUTING ORGANIZATION\n")
            
        # Create structure
        self.create_unified_structure()
        
        # Organize each source folder
        self.organize_datax()
        self.organize_neo4j()
        self.organize_neo4j_data()
        self.organize_nvd()
        
        if not dry_run:
            # Cleanup and documentation
            self.cleanup_empty_folders()
            self.create_master_readme()
            
        # Summary
        self.print_summary()
        
        if dry_run:
            logger.info("\n💡 To execute these changes, run: python organize_all_folders.py --execute")


if __name__ == "__main__":
    import sys
    
    workspace = Path(__file__).parent.parent
    organizer = AdvancedOrganizer(workspace)
    
    # Check for --execute flag
    execute = "--execute" in sys.argv
    
    organizer.execute(dry_run=not execute)
