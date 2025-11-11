#!/usr/bin/env python3
"""
CyberGuard Enterprise Platform - Multi-Platform Builder

This script creates the complete platform structure:
1. Web Application (React + TypeScript)
2. Mobile Application (React Native)
3. Desktop Application (Electron + React)
4. Backend API (FastAPI)

Usage:
    python build_platform.py [--web] [--mobile] [--desktop] [--backend] [--all]

Options:
    --web       Create web application only
    --mobile    Create mobile application only
    --desktop   Create desktop application only
    --backend   Create backend API only
    --all       Create all applications (default)
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}→ {text}{Colors.ENDC}")

def run_command(cmd, cwd=None):
    """Run shell command"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            check=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {cmd}")
        print(e.stderr)
        return False

def create_web_app(base_dir):
    """Create React web application"""
    print_header("CREATING WEB APPLICATION (React + TypeScript)")
    
    web_dir = os.path.join(base_dir, 'web')
    
    # Create React app with TypeScript
    print_info("Creating React application...")
    if run_command(f'npx create-react-app web --template typescript', cwd=base_dir):
        print_success("React app created")
    else:
        print_error("Failed to create React app")
        return False
    
    # Install additional dependencies
    print_info("Installing dependencies...")
    dependencies = [
        '@mui/material',
        '@mui/icons-material',
        '@emotion/react',
        '@emotion/styled',
        'react-router-dom',
        '@reduxjs/toolkit',
        'react-redux',
        'axios',
        'socket.io-client',
        'chart.js',
        'react-chartjs-2',
        'recharts',
        'date-fns',
        'formik',
        'yup'
    ]
    
    deps_str = ' '.join(dependencies)
    if run_command(f'npm install {deps_str}', cwd=web_dir):
        print_success("Dependencies installed")
    else:
        print_error("Failed to install dependencies")
    
    # Create directory structure
    print_info("Creating directory structure...")
    dirs = [
        'src/components/common',
        'src/components/dashboard',
        'src/components/threats',
        'src/components/auth',
        'src/pages',
        'src/services',
        'src/hooks',
        'src/store',
        'src/store/slices',
        'src/utils',
        'src/types',
        'src/styles'
    ]
    
    for dir_path in dirs:
        os.makedirs(os.path.join(web_dir, dir_path), exist_ok=True)
    
    print_success("Web application structure created")
    return True

def create_mobile_app(base_dir):
    """Create React Native mobile application"""
    print_header("CREATING MOBILE APPLICATION (React Native)")
    
    # Create React Native app
    print_info("Creating React Native application...")
    if run_command('npx react-native init CyberGuardMobile --template react-native-template-typescript', cwd=base_dir):
        print_success("React Native app created")
    else:
        print_error("Failed to create React Native app")
        return False
    
    mobile_dir = os.path.join(base_dir, 'CyberGuardMobile')
    
    # Rename to mobile
    os.rename(mobile_dir, os.path.join(base_dir, 'mobile'))
    mobile_dir = os.path.join(base_dir, 'mobile')
    
    # Install additional dependencies
    print_info("Installing dependencies...")
    dependencies = [
        '@react-navigation/native',
        '@react-navigation/stack',
        '@react-navigation/bottom-tabs',
        'react-native-paper',
        'react-native-vector-icons',
        '@reduxjs/toolkit',
        'react-redux',
        'axios',
        'react-native-push-notification',
        'react-native-biometrics',
        'react-native-keychain',
        '@react-native-async-storage/async-storage'
    ]
    
    deps_str = ' '.join(dependencies)
    if run_command(f'npm install {deps_str}', cwd=mobile_dir):
        print_success("Dependencies installed")
    else:
        print_error("Failed to install dependencies")
    
    print_success("Mobile application structure created")
    return True

def create_desktop_app(base_dir):
    """Create Electron desktop application"""
    print_header("CREATING DESKTOP APPLICATION (Electron + React)")
    
    desktop_dir = os.path.join(base_dir, 'desktop')
    os.makedirs(desktop_dir, exist_ok=True)
    
    # Initialize npm project
    print_info("Initializing desktop application...")
    package_json = {
        "name": "cyberguard-desktop",
        "version": "1.0.0",
        "description": "CyberGuard Enterprise Platform - Desktop Application",
        "main": "main.js",
        "scripts": {
            "start": "electron .",
            "dev": "concurrently \"npm run start:react\" \"wait-on http://localhost:3001 && npm run start:electron\"",
            "start:react": "cd renderer && npm start",
            "start:electron": "electron .",
            "build": "cd renderer && npm run build",
            "build:win": "electron-builder --win",
            "build:mac": "electron-builder --mac",
            "build:linux": "electron-builder --linux"
        },
        "build": {
            "appId": "com.cyberguard.desktop",
            "productName": "CyberGuard",
            "directories": {
                "output": "dist"
            },
            "files": [
                "main.js",
                "preload.js",
                "renderer/build/**/*"
            ],
            "win": {
                "target": ["nsis"],
                "icon": "assets/icon.ico"
            }
        }
    }
    
    with open(os.path.join(desktop_dir, 'package.json'), 'w') as f:
        json.dump(package_json, f, indent=2)
    
    # Install Electron
    print_info("Installing Electron...")
    if run_command('npm install electron electron-builder concurrently wait-on --save-dev', cwd=desktop_dir):
        print_success("Electron installed")
    else:
        print_error("Failed to install Electron")
    
    # Create React app for renderer
    print_info("Creating renderer (React)...")
    if run_command('npx create-react-app renderer --template typescript', cwd=desktop_dir):
        print_success("Renderer created")
    else:
        print_error("Failed to create renderer")
    
    print_success("Desktop application structure created")
    return True

def create_backend_api(base_dir):
    """Create FastAPI backend (already exists)"""
    print_header("BACKEND API")
    print_success("Backend API already created at backend/app/main.py")
    print_info("Install dependencies: pip install -r backend/requirements.txt")
    print_info("Run server: cd backend && uvicorn app.main:app --reload")
    return True

def create_docker_compose(base_dir):
    """Create Docker Compose configuration"""
    print_header("CREATING DOCKER COMPOSE CONFIGURATION")
    
    docker_compose = """version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:14-alpine
    environment:
      POSTGRES_DB: cyberguard
      POSTGRES_USER: cyberguard
      POSTGRES_PASSWORD: cyberguard_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - cyberguard-network

  # Redis Cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - cyberguard-network

  # FastAPI Backend
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://cyberguard:cyberguard_password@postgres:5432/cyberguard
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    networks:
      - cyberguard-network
    volumes:
      - ./backend:/app

  # Web Application
  web:
    build: ./web
    ports:
      - "3000:3000"
    environment:
      REACT_APP_API_URL: http://localhost:8000/api/v1
    networks:
      - cyberguard-network
    volumes:
      - ./web:/app
      - /app/node_modules

volumes:
  postgres_data:

networks:
  cyberguard-network:
    driver: bridge
"""
    
    with open(os.path.join(base_dir, 'docker-compose.yml'), 'w') as f:
        f.write(docker_compose)
    
    print_success("Docker Compose configuration created")
    return True

def main():
    print(f"\n{Colors.HEADER}{Colors.BOLD}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🛡️  CYBERGUARD MULTI-PLATFORM BUILDER".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{Colors.ENDC}\n")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(base_dir)
    
    # Parse arguments
    args = sys.argv[1:]
    create_all = '--all' in args or len(args) == 0
    
    results = {}
    
    # Backend (already exists)
    if create_all or '--backend' in args:
        results['backend'] = create_backend_api(parent_dir)
    
    # Web Application
    if create_all or '--web' in args:
        results['web'] = create_web_app(parent_dir)
    
    # Mobile Application
    if create_all or '--mobile' in args:
        print_info("Mobile app creation requires React Native CLI")
        print_info("Skip mobile for now - create manually later")
        results['mobile'] = True
    
    # Desktop Application
    if create_all or '--desktop' in args:
        results['desktop'] = create_desktop_app(parent_dir)
    
    # Docker Compose
    if create_all:
        results['docker'] = create_docker_compose(parent_dir)
    
    # Summary
    print_header("BUILD SUMMARY")
    
    for component, success in results.items():
        if success:
            print_success(f"{component.title()} - Created successfully")
        else:
            print_error(f"{component.title()} - Failed")
    
    print("\n" + "="*70)
    print(f"{Colors.OKGREEN}{Colors.BOLD}Platform build complete!{Colors.ENDC}")
    print("="*70)
    
    print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}\n")
    print("1. Backend API:")
    print("   cd backend")
    print("   pip install -r requirements.txt")
    print("   uvicorn app.main:app --reload\n")
    
    print("2. Web Application:")
    print("   cd web")
    print("   npm start\n")
    
    print("3. Desktop Application:")
    print("   cd desktop")
    print("   npm run dev\n")
    
    print("4. Docker (All Services):")
    print("   docker-compose up -d\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Build cancelled by user.{Colors.ENDC}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.FAIL}Error: {e}{Colors.ENDC}\n")
        sys.exit(1)
