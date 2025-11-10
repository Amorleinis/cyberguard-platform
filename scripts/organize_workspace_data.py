"""
CyberGuard Industries - Data Organization Script
Lance Brady & AI Collaboration

This script organizes all workspace data files into a structured hierarchy:
- CVE data → data/cve/
- MITRE ATT&CK → data/mitre/
- Threat intelligence → data/intelligence/
- Malware/hashes → data/malware/
- Neo4j data → data/neo4j/
- Scenarios → data/scenarios/
- Processed data → data/processed/
"""

import shutil
import json
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataOrganizer:
    """Organize workspace data files"""
    
    def __init__(self, workspace_root: str):
        self.root = Path(workspace_root)
        self.data_root = self.root / "data"
        
        # Define target structure
        self.structure = {
            'cve': self.data_root / 'cve',
            'mitre': self.data_root / 'mitre',
            'intelligence': self.data_root / 'intelligence',
            'malware': self.data_root / 'malware',
            'neo4j': self.data_root / 'neo4j',
            'scenarios': self.data_root / 'scenarios',
            'processed': self.data_root / 'processed',
            'raw': self.data_root / 'raw',
            'nvd': self.data_root / 'nvd',
            'logs': self.data_root / 'logs'
        }
        
        self.operations = []
        self.dry_run = True
    
    def create_structure(self):
        """Create organized directory structure"""
        logger.info("Creating organized directory structure...")
        
        for category, path in self.structure.items():
            if not self.dry_run:
                path.mkdir(parents=True, exist_ok=True)
            logger.info(f"  📁 {category.upper()}: {path.relative_to(self.root)}")
        
        # Create subdirectories
        subdirs = {
            'cve': ['2020', '2021', '2022', '2023', '2024', 'merged', 'with_use_cases'],
            'mitre': ['attack_patterns', 'techniques', 'tactics', 'actors', 'groups'],
            'intelligence': ['processed', 'enriched', 'reports'],
            'malware': ['hashes', 'signatures', 'samples'],
            'neo4j': ['nodes', 'relationships', 'exports'],
            'scenarios': ['blue_team', 'red_team', 'logs', 'analytics'],
            'nvd': ['feeds', 'processed', 'metrics']
        }
        
        for category, subs in subdirs.items():
            base_path = self.structure.get(category)
            if base_path:
                for sub in subs:
                    sub_path = base_path / sub
                    if not self.dry_run:
                        sub_path.mkdir(parents=True, exist_ok=True)
                    logger.info(f"    └─ {sub}")
    
    def organize_cve_files(self):
        """Organize CVE data files"""
        logger.info("\n📊 Organizing CVE data files...")
        
        cve_files = {
            'cve_data.json': 'raw',
            'cve_data_2020_2024_merged.json': 'merged',
            'cve_data_2020_2024_with_use_cases.json': 'with_use_cases',
            'cve_data_with_use_cases.json': 'with_use_cases'
        }
        
        for filename, category in cve_files.items():
            source = self.root / filename
            if source.exists():
                if category == 'merged':
                    target = self.structure['cve'] / 'merged' / filename
                elif category == 'with_use_cases':
                    target = self.structure['cve'] / 'with_use_cases' / filename
                else:
                    target = self.structure['cve'] / category / filename
                
                self.operations.append(('move', source, target))
                logger.info(f"  {filename} → {target.relative_to(self.root)}")
    
    def organize_nvd_files(self):
        """Organize NVD directory files"""
        logger.info("\n🗃️ Organizing NVD files...")
        
        nvd_source = self.root / 'NVD'
        if nvd_source.exists():
            # Move processed files
            for file in nvd_source.glob('nvd_*_processed.*'):
                target = self.structure['nvd'] / 'processed' / file.name
                self.operations.append(('move', file, target))
                logger.info(f"  {file.name} → nvd/processed/")
            
            # Move further subdirectory
            further_dir = nvd_source / 'further'
            if further_dir.exists():
                target = self.structure['nvd'] / 'further'
                self.operations.append(('move', further_dir, target))
                logger.info(f"  further/ → nvd/further/")
    
    def organize_neo4j_files(self):
        """Organize Neo4j data files"""
        logger.info("\n🔗 Organizing Neo4j data...")
        
        # Main neo4j directory
        neo4j_source = self.root / 'neo4j'
        if neo4j_source.exists():
            # Categorize by file type
            for csv_file in neo4j_source.glob('*.csv'):
                # Determine category based on filename
                if 'actor' in csv_file.name.lower():
                    category = 'actors'
                elif any(x in csv_file.name.lower() for x in ['attack', 'threat', 'action']):
                    category = 'attack_patterns'
                elif any(x in csv_file.name.lower() for x in ['asset', 'signal', 'control']):
                    category = 'nodes'
                else:
                    category = 'relationships'
                
                target = self.structure['neo4j'] / category / csv_file.name
                self.operations.append(('move', csv_file, target))
                logger.info(f"  {csv_file.name} → neo4j/{category}/")
        
        # neo4j_data directory
        neo4j_data_source = self.root / 'neo4j_data'
        if neo4j_data_source.exists():
            for file in neo4j_data_source.glob('*'):
                if file.is_file():
                    target = self.structure['mitre'] / 'attack_patterns' / file.name
                    self.operations.append(('move', file, target))
                    logger.info(f"  {file.name} → mitre/attack_patterns/")
    
    def organize_scenario_files(self):
        """Organize enhanced scenarios"""
        logger.info("\n🎯 Organizing scenario files...")
        
        scenarios_source = self.root / 'enhanced_scenarios'
        if scenarios_source.exists():
            # Move markdown scenarios
            for md_file in scenarios_source.glob('*.md'):
                if 'blue_team' in md_file.name:
                    target = self.structure['scenarios'] / 'blue_team' / md_file.name
                elif 'red_team' in md_file.name:
                    target = self.structure['scenarios'] / 'red_team' / md_file.name
                else:
                    target = self.structure['scenarios'] / md_file.name
                
                self.operations.append(('move', md_file, target))
                logger.info(f"  {md_file.name} → scenarios/...")
            
            # Move logs
            logs_dir = scenarios_source / 'logs'
            if logs_dir.exists():
                for log_file in logs_dir.glob('*.json'):
                    target = self.structure['scenarios'] / 'logs' / log_file.name
                    self.operations.append(('move', log_file, target))
                logger.info(f"  logs/*.json → scenarios/logs/ ({len(list(logs_dir.glob('*.json')))} files)")
            
            # Move analytics
            for csv_file in scenarios_source.glob('*.csv'):
                target = self.structure['scenarios'] / 'analytics' / csv_file.name
                self.operations.append(('move', csv_file, target))
                logger.info(f"  {csv_file.name} → scenarios/analytics/")
    
    def organize_processed_data(self):
        """Organize processed/enriched data"""
        logger.info("\n⚙️ Organizing processed data...")
        
        # Data directory enriched results
        data_dir = self.root / 'data'
        if data_dir.exists():
            for file in data_dir.glob('enriched*.json'):
                target = self.structure['intelligence'] / 'enriched' / file.name
                self.operations.append(('move', file, target))
                logger.info(f"  {file.name} → intelligence/enriched/")
        
        # Engine-specific processed data
        engine_dirs = ['intelligence', 'prevention', 'detection', 'response', 'isolation', 'mitigation', 'recovery']
        for engine in engine_dirs:
            engine_path = self.root / engine
            if engine_path.exists():
                for json_file in engine_path.glob('*_enhanced.json'):
                    target = self.structure['processed'] / engine / json_file.name
                    self.operations.append(('move', json_file, target))
                    logger.info(f"  {json_file.name} → processed/{engine}/")
                
                for json_file in engine_path.glob('processed_*.json'):
                    target = self.structure['processed'] / engine / json_file.name
                    self.operations.append(('move', json_file, target))
                    logger.info(f"  {json_file.name} → processed/{engine}/")
    
    def organize_malware_data(self):
        """Organize malware and hash data"""
        logger.info("\n🦠 Organizing malware data...")
        
        # Check NVD for malware files
        nvd_dir = self.root / 'NVD'
        if nvd_dir.exists():
            for file in nvd_dir.glob('*malware*'):
                target = self.structure['malware'] / 'hashes' / file.name
                self.operations.append(('move', file, target))
                logger.info(f"  {file.name} → malware/hashes/")
            
            for file in nvd_dir.glob('*hash*'):
                target = self.structure['malware'] / 'hashes' / file.name
                self.operations.append(('move', file, target))
                logger.info(f"  {file.name} → malware/hashes/")
    
    def create_index_files(self):
        """Create index/README files for each category"""
        logger.info("\n📝 Creating index files...")
        
        indexes = {
            'cve': {
                'title': 'CVE Vulnerability Data',
                'description': 'Common Vulnerabilities and Exposures database (2020-2024)',
                'files': ['merged/', 'with_use_cases/', 'raw/']
            },
            'mitre': {
                'title': 'MITRE ATT&CK Framework Data',
                'description': 'Attack patterns, techniques, tactics, and threat actors',
                'files': ['attack_patterns/', 'techniques/', 'actors/']
            },
            'intelligence': {
                'title': 'Threat Intelligence',
                'description': 'Processed and enriched threat intelligence data',
                'files': ['processed/', 'enriched/', 'reports/']
            },
            'malware': {
                'title': 'Malware Database',
                'description': 'Malware signatures, hashes, and samples',
                'files': ['hashes/', 'signatures/']
            },
            'scenarios': {
                'title': 'Security Scenarios',
                'description': 'Blue team and red team exercise scenarios',
                'files': ['blue_team/', 'red_team/', 'logs/', 'analytics/']
            },
            'nvd': {
                'title': 'NVD (National Vulnerability Database)',
                'description': 'NVD feeds and processed vulnerability data',
                'files': ['feeds/', 'processed/', 'metrics/']
            }
        }
        
        for category, info in indexes.items():
            index_path = self.structure[category] / 'README.md'
            content = f"""# {info['title']}

{info['description']}

## Structure

"""
            for folder in info['files']:
                content += f"- `{folder}` - {self._get_folder_description(category, folder)}\n"
            
            content += f"""
## Last Updated

{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Managed By

CyberGuard Industries - Lance Brady & AI Collaboration
"""
            
            if not self.dry_run:
                with open(index_path, 'w') as f:
                    f.write(content)
            
            logger.info(f"  Created {category}/README.md")
    
    def _get_folder_description(self, category, folder):
        """Get description for folder"""
        descriptions = {
            'cve': {
                'merged/': 'Merged CVE datasets across years',
                'with_use_cases/': 'CVEs with practical use cases',
                'raw/': 'Raw CVE data files'
            },
            'mitre': {
                'attack_patterns/': 'MITRE ATT&CK attack patterns',
                'techniques/': 'Attack techniques and procedures',
                'actors/': 'Threat actor profiles'
            },
            'intelligence': {
                'processed/': 'Processed threat intelligence',
                'enriched/': 'Enriched with IOCs and context',
                'reports/': 'Intelligence reports'
            }
        }
        
        return descriptions.get(category, {}).get(folder, 'Data files')
    
    def generate_summary(self):
        """Generate organization summary"""
        logger.info("\n" + "=" * 80)
        logger.info("ORGANIZATION SUMMARY")
        logger.info("=" * 80)
        
        # Count operations by type
        move_count = sum(1 for op in self.operations if op[0] == 'move')
        
        logger.info(f"\nTotal operations planned: {len(self.operations)}")
        logger.info(f"  • Files to move: {move_count}")
        
        # Count by category
        categories = {}
        for op_type, source, target in self.operations:
            category = target.parent.parent.name if target.parent.parent != self.data_root else target.parent.name
            categories[category] = categories.get(category, 0) + 1
        
        logger.info(f"\nFiles per category:")
        for category, count in sorted(categories.items()):
            logger.info(f"  • {category}: {count} files")
        
        logger.info("\n" + "=" * 80)
    
    def execute(self, dry_run=True):
        """Execute organization plan"""
        self.dry_run = dry_run
        
        logger.info("=" * 80)
        logger.info("CyberGuard Industries - Data Organization")
        logger.info("=" * 80)
        logger.info(f"Mode: {'DRY RUN (preview only)' if dry_run else 'EXECUTE (files will be moved)'}")
        logger.info(f"Workspace: {self.root}")
        logger.info("")
        
        # Plan operations
        self.create_structure()
        self.organize_cve_files()
        self.organize_nvd_files()
        self.organize_neo4j_files()
        self.organize_scenario_files()
        self.organize_processed_data()
        self.organize_malware_data()
        self.create_index_files()
        
        # Generate summary
        self.generate_summary()
        
        # Execute if not dry run
        if not dry_run:
            logger.info("\n🔄 Executing file operations...")
            
            success_count = 0
            error_count = 0
            
            for op_type, source, target in self.operations:
                try:
                    if op_type == 'move':
                        # Create parent directory
                        target.parent.mkdir(parents=True, exist_ok=True)
                        
                        # Move file or directory
                        shutil.move(str(source), str(target))
                        success_count += 1
                        
                except Exception as e:
                    logger.error(f"  ❌ Error moving {source.name}: {e}")
                    error_count += 1
            
            logger.info(f"\n✅ Complete: {success_count} successful, {error_count} errors")
        else:
            logger.info("\n⚠️  DRY RUN - No files were moved")
            logger.info("   Run with execute(dry_run=False) to apply changes")

def main():
    """Main execution"""
    import sys
    
    workspace_root = Path(__file__).parent.parent
    organizer = DataOrganizer(workspace_root)
    
    # Check for --execute flag
    execute = '--execute' in sys.argv
    
    organizer.execute(dry_run=not execute)
    
    if not execute:
        print("\n" + "=" * 80)
        print("To execute these changes, run:")
        print(f"  python {Path(__file__).name} --execute")
        print("=" * 80)

if __name__ == "__main__":
    main()
