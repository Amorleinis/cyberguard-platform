#!/usr/bin/env python3
"""
CyberGuard Enterprise Platform - Professional Installer
Automated installation and configuration script
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import json

VERSION = "2.0.0"
BANNER = """
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           CyberGuard Enterprise Platform v{version}              ║
║           Professional Installation Wizard                    ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
""".format(version=VERSION)


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_banner():
    """Print installation banner"""
    print(Colors.CYAN + BANNER + Colors.END)


def print_step(message):
    """Print installation step"""
    print(f"\n{Colors.BOLD}[{Colors.CYAN}•{Colors.END}{Colors.BOLD}] {message}{Colors.END}")


def print_success(message):
    """Print success message"""
    print(f"{Colors.GREEN}✓{Colors.END} {message}")


def print_error(message):
    """Print error message"""
    print(f"{Colors.RED}✗{Colors.END} {message}")


def print_warning(message):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.END} {message}")


def check_python_version():
    """Check if Python version is compatible"""
    print_step("Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python 3.8+ required. Found: {sys.version.split()[0]}")
        return False
    
    print_success(f"Python {sys.version.split()[0]} detected")
    return True


def check_system_requirements():
    """Check system requirements"""
    print_step("Checking system requirements...")
    
    # Check OS
    os_name = platform.system()
    print_success(f"Operating System: {os_name}")
    
    # Check available disk space
    import shutil
    disk = shutil.disk_usage(Path.cwd())
    free_gb = disk.free / (1024**3)
    
    if free_gb < 10:
        print_warning(f"Low disk space: {free_gb:.1f}GB available (10GB recommended)")
    else:
        print_success(f"Disk space: {free_gb:.1f}GB available")
    
    return True


def create_virtual_environment():
    """Create Python virtual environment"""
    print_step("Creating virtual environment...")
    
    venv_path = Path('.venv')
    if venv_path.exists():
        print_warning("Virtual environment already exists. Skipping...")
        return True
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', '.venv'], check=True)
        print_success("Virtual environment created")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Failed to create virtual environment: {e}")
        return False


def get_pip_command():
    """Get the pip command based on OS"""
    if platform.system() == 'Windows':
        return str(Path('.venv') / 'Scripts' / 'pip.exe')
    else:
        return str(Path('.venv') / 'bin' / 'pip')


def install_dependencies(edition='core'):
    """Install Python dependencies"""
    print_step(f"Installing {edition} dependencies...")
    
    pip_cmd = get_pip_command()
    
    requirements_files = {
        'core': ['requirements.txt'],
        'ml': ['requirements.txt', 'requirements-ml.txt'],
        'performance': ['requirements.txt', 'requirements-performance.txt'],
        'enterprise': ['requirements.txt', 'requirements-ml.txt', 'requirements-performance.txt'],
        'dev': ['requirements.txt', 'requirements-dev.txt']
    }
    
    files = requirements_files.get(edition, ['requirements.txt'])
    
    for req_file in files:
        if not Path(req_file).exists():
            print_warning(f"{req_file} not found, skipping...")
            continue
        
        print(f"   Installing from {req_file}...")
        try:
            subprocess.run([pip_cmd, 'install', '-r', req_file], check=True, capture_output=True)
            print_success(f"{req_file} installed")
        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install from {req_file}")
            return False
    
    return True


def create_directory_structure():
    """Create necessary directories"""
    print_step("Creating directory structure...")
    
    directories = [
        'data/cache',
        'data/config',
        'data/logs',
        'data/ml_models',
        'data/reports',
        'data/quarantine',
        'data/backups',
        'logs',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print_success(f"{len(directories)} directories created")
    return True


def create_default_config():
    """Create default configuration files"""
    print_step("Creating default configuration...")
    
    config = {
        "platform": {
            "version": VERSION,
            "edition": "enterprise",
            "install_date": str(Path.cwd())
        },
        "monitoring": {
            "scan_interval_seconds": 60,
            "enable_network_scan": True,
            "enable_process_scan": True,
            "enable_file_scan": True
        },
        "ml_detection": {
            "enable_anomaly_detection": True,
            "confidence_threshold": 0.8,
            "auto_retrain": True
        },
        "performance": {
            "worker_threads": 8,
            "enable_caching": True,
            "cache_ttl_seconds": 3600
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "enable_cors": True
        },
        "dashboard": {
            "host": "0.0.0.0",
            "port": 5000
        }
    }
    
    config_file = Path('data/config/platform_config.json')
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print_success("Configuration file created")
    return True


def install_cli_tools():
    """Install CLI tools"""
    print_step("Installing CLI tools...")
    
    pip_cmd = get_pip_command()
    
    try:
        subprocess.run([pip_cmd, 'install', 'click>=8.1.0'], check=True, capture_output=True)
        print_success("CLI tools installed")
        return True
    except subprocess.CalledProcessError:
        print_error("Failed to install CLI tools")
        return False


def run_tests():
    """Run basic platform tests"""
    print_step("Running platform tests...")
    
    tests = [
        ("Import core modules", lambda: __import__('scripts.active_threat_monitor')),
        ("Check data directories", lambda: Path('data').exists()),
        ("Verify configuration", lambda: Path('data/config/platform_config.json').exists()),
    ]
    
    passed = 0
    for test_name, test_func in tests:
        try:
            test_func()
            print_success(f"{test_name}")
            passed += 1
        except Exception as e:
            print_error(f"{test_name}: {str(e)}")
    
    print(f"\n   {passed}/{len(tests)} tests passed")
    return passed == len(tests)


def print_next_steps():
    """Print post-installation instructions"""
    print("\n" + "="*70)
    print(f"{Colors.GREEN}{Colors.BOLD}✓ Installation Complete!{Colors.END}\n")
    
    print(f"{Colors.BOLD}Next Steps:{Colors.END}\n")
    
    if platform.system() == 'Windows':
        activate_cmd = ".venv\\Scripts\\activate"
    else:
        activate_cmd = "source .venv/bin/activate"
    
    steps = [
        ("1. Activate virtual environment:", activate_cmd),
        ("2. View platform status:", "python scripts/cli.py status"),
        ("3. Start web dashboard:", "python scripts/cli.py start dashboard"),
        ("4. Start API server:", "python scripts/cli.py start api"),
        ("5. Run platform demo:", "python scripts/cli.py demo"),
        ("6. View help:", "python scripts/cli.py --help"),
    ]
    
    for step, command in steps:
        print(f"   {Colors.CYAN}{step}{Colors.END}")
        print(f"   {Colors.BOLD}${Colors.END} {command}\n")
    
    print(f"{Colors.BOLD}Documentation:{Colors.END}")
    print(f"   📚 README: README_ULTIMATE.md")
    print(f"   📖 Docs: docs/")
    print(f"   🌐 Website: https://cyberguard-platform.com\n")
    
    print("="*70 + "\n")


def main():
    """Main installation process"""
    print_banner()
    
    print(f"{Colors.BOLD}Welcome to the CyberGuard Enterprise Platform installer!{Colors.END}")
    print(f"This wizard will guide you through the installation process.\n")
    
    # Prompt for edition
    print(f"{Colors.BOLD}Select Edition:{Colors.END}")
    print("  1. Core (Free - Basic features)")
    print("  2. Professional (ML + Analytics)")
    print("  3. Enterprise (ML + Analytics + Performance)")
    print("  4. Development (All features + dev tools)")
    
    edition_map = {
        '1': 'core',
        '2': 'ml',
        '3': 'enterprise',
        '4': 'dev'
    }
    
    choice = input(f"\nEnter choice [1-4] (default: 1): ").strip() or '1'
    edition = edition_map.get(choice, 'core')
    
    print(f"\n{Colors.GREEN}Installing {edition.title()} Edition...{Colors.END}\n")
    
    # Run installation steps
    steps = [
        check_python_version,
        check_system_requirements,
        create_virtual_environment,
        lambda: install_dependencies(edition),
        create_directory_structure,
        create_default_config,
        install_cli_tools,
    ]
    
    for step in steps:
        if not step():
            print_error("\nInstallation failed!")
            sys.exit(1)
    
    # Optional: Run tests
    print(f"\n{Colors.BOLD}Would you like to run platform tests? (y/n):{Colors.END} ", end='')
    if input().lower() == 'y':
        run_tests()
    
    print_next_steps()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Installation cancelled by user.{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"\nUnexpected error: {str(e)}")
        sys.exit(1)
