"""
Final Consolidation Script
Moves all remaining content from DATAX, neo4j, neo4j_data into data/
"""

import os
import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FinalConsolidator:
    """Final cleanup and consolidation"""
    
    def __init__(self, workspace_root):
        self.workspace_root = Path(workspace_root)
        self.data_root = self.workspace_root / "data"
        self.moved_count = 0
        
    def consolidate_datax_data(self):
        """Move DATAX/data/ contents into data/"""
        logger.info("\n📂 Consolidating DATAX/data/...")
        
        datax_data = self.workspace_root / "DATAX" / "data"
        if not datax_data.exists():
            logger.warning("DATAX/data not found")
            return
            
        # Move all subdirectories and files
        for item in datax_data.iterdir():
            if item.name == '__pycache__':
                continue
                
            dest = self.data_root / item.name
            
            if dest.exists():
                logger.info(f"  🔀 Merging: {item.name}/")
                # Merge contents
                if item.is_dir():
                    self._merge_directories(item, dest)
                else:
                    logger.info(f"  ⏭️  Skipped (exists): {item.name}")
            else:
                logger.info(f"  ✓ Moving: {item.name}")
                shutil.move(str(item), str(dest))
                self.moved_count += 1
                
    def consolidate_neo4j_data(self):
        """Move neo4j_data/ into data/neo4j/database_files/"""
        logger.info("\n💾 Consolidating neo4j_data/...")
        
        neo4j_data_src = self.workspace_root / "neo4j_data"
        if not neo4j_data_src.exists():
            logger.warning("neo4j_data not found")
            return
            
        neo4j_dest = self.data_root / "neo4j" / "database_files"
        neo4j_dest.mkdir(parents=True, exist_ok=True)
        
        # Move database directories
        for item in neo4j_data_src.iterdir():
            dest = neo4j_dest / item.name
            
            if dest.exists():
                logger.info(f"  ⏭️  Already exists: {item.name}/")
            else:
                logger.info(f"  ✓ Moving: {item.name}/")
                shutil.move(str(item), str(dest))
                self.moved_count += 1
                
    def consolidate_neo4j_folders(self):
        """Move neo4j/ scripts and folders into data/neo4j/"""
        logger.info("\n🔷 Consolidating neo4j/...")
        
        neo4j_src = self.workspace_root / "neo4j"
        if not neo4j_src.exists():
            logger.warning("neo4j folder not found")
            return
            
        neo4j_dest = self.data_root / "neo4j"
        neo4j_dest.mkdir(parents=True, exist_ok=True)
        
        for item in neo4j_src.iterdir():
            if item.name == '__pycache__':
                continue
                
            dest = neo4j_dest / item.name
            
            if dest.exists():
                logger.info(f"  ⏭️  Already exists: {item.name}")
                if item.is_dir():
                    self._merge_directories(item, dest)
            else:
                logger.info(f"  ✓ Moving: {item.name}")
                shutil.move(str(item), str(dest))
                self.moved_count += 1
                
    def _merge_directories(self, src_dir, dest_dir):
        """Merge source directory into destination"""
        for item in src_dir.rglob('*'):
            if '__pycache__' in str(item):
                continue
                
            if item.is_file():
                rel_path = item.relative_to(src_dir)
                dest_file = dest_dir / rel_path
                
                if not dest_file.exists():
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    try:
                        # Use move instead of copy for OneDrive compatibility
                        shutil.move(str(item), str(dest_file))
                        logger.info(f"    ↳ {rel_path}")
                        self.moved_count += 1
                    except Exception as e:
                        logger.warning(f"    ⚠️  Could not move {rel_path}: {e}")
                        # Try copy as fallback
                        try:
                            shutil.copy2(str(item), str(dest_file))
                            logger.info(f"    ↳ {rel_path} (copied)")
                            self.moved_count += 1
                        except Exception as e2:
                            logger.error(f"    ✗ Failed: {rel_path}: {e2}")
                    
    def cleanup_empty_folders(self):
        """Remove empty source folders"""
        logger.info("\n🧹 Cleaning up empty folders...")
        
        folders_to_remove = ['DATAX', 'neo4j', 'neo4j_data']
        
        for folder_name in folders_to_remove:
            folder_path = self.workspace_root / folder_name
            if folder_path.exists():
                try:
                    # Remove __pycache__ first
                    for pycache in folder_path.rglob('__pycache__'):
                        shutil.rmtree(pycache, ignore_errors=True)
                    
                    # Check if empty now
                    if not any(folder_path.rglob('*')):
                        shutil.rmtree(folder_path)
                        logger.info(f"  ✓ Removed: {folder_name}/")
                    else:
                        remaining = list(folder_path.rglob('*'))[:5]
                        logger.warning(f"  ⚠️  {folder_name}/ still has {len(list(folder_path.rglob('*')))} items")
                        for item in remaining:
                            logger.warning(f"      - {item.relative_to(folder_path)}")
                            
                except Exception as e:
                    logger.error(f"  ✗ Error removing {folder_name}: {e}")
                    
    def create_consolidation_report(self):
        """Create a report of the final structure"""
        logger.info("\n📝 Creating consolidation report...")
        
        report = f"""# Final Workspace Consolidation Report
**Completed:** {self.moved_count} items consolidated

## Consolidated Folders

All data from the following scattered folders has been merged into `data/`:

- ✅ **DATAX/** → Merged into `data/`
  - DATAX/data/nvd/ → data/nvd/
  - DATAX/data/processed/ → data/datasets/processed/
  - DATAX/data/raw/ → data/datasets/raw/
  - DATAX/data/exports/ → data/datasets/exports/

- ✅ **neo4j/** → Moved to `data/neo4j/`
  - Scripts, nodes, graph data

- ✅ **neo4j_data/** → Moved to `data/neo4j/database_files/`
  - databases/, dbms/, transactions/

## Final Unified Structure

```
data/
├── cve/                    - CVE datasets (organized earlier)
├── mitre/                  - MITRE ATT&CK data
├── intelligence/           - Threat intelligence
├── neo4j/                  - 🆕 All Neo4j content
│   ├── scripts/
│   ├── nodes/
│   ├── graph_data/
│   └── database_files/     - 🆕 From neo4j_data/
├── nvd/                    - 🆕 Merged NVD data
│   ├── feeds/
│   └── processed/
├── datasets/               - 🆕 Training datasets
│   ├── raw/
│   ├── processed/          - 🆕 From DATAX/data/processed/
│   ├── features/
│   ├── taxonomy/
│   └── exports/            - 🆕 From DATAX/data/exports/
├── ml_models/              - ML training artifacts
├── scenarios/              - Security scenarios
├── visualizations/         - Charts and dashboards
├── config/                 - Configuration files
├── tools/                  - Utility scripts
└── archive/                - Legacy projects
```

## Workspace Root (Clean)

After consolidation, your workspace root only contains:

- `data/` - **ALL data in one place**
- `detection/`, `intelligence/`, `isolation/`, etc. - Engine packages
- `demos/`, `docs/`, `scripts/`, `tests/` - Support files
- `.venv/` - Python environment
- Setup files (setup.py, requirements.txt, README.md)

---
*All scattered data folders have been unified into `data/`*
"""
        
        report_path = self.workspace_root / "CONSOLIDATION_COMPLETE.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
            
        logger.info(f"  ✓ Created {report_path.name}")
        
    def execute(self):
        """Run the final consolidation"""
        logger.info("🚀 FINAL CONSOLIDATION\n")
        logger.info("="*80)
        
        self.consolidate_datax_data()
        self.consolidate_neo4j_folders()
        self.consolidate_neo4j_data()
        self.cleanup_empty_folders()
        self.create_consolidation_report()
        
        logger.info("\n" + "="*80)
        logger.info(f"✅ CONSOLIDATION COMPLETE!")
        logger.info(f"📊 Total items moved: {self.moved_count}")
        logger.info("="*80)


if __name__ == "__main__":
    workspace = Path(__file__).parent.parent
    consolidator = FinalConsolidator(workspace)
    consolidator.execute()
