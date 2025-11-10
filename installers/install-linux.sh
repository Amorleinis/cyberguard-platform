#!/bin/bash
# CyberGuard Enterprise Platform - Linux Installer
# Installation script for Linux systems (Ubuntu/Debian/RHEL/CentOS)

set -e

VERSION="2.0.0"
INSTALL_DIR="/opt/cyberguard"
EDITION="core"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Banner
show_banner() {
    echo -e "${CYAN}"
    cat << "EOF"

╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║           CyberGuard Enterprise Platform v2.0.0               ║
║           Linux Installation Script                           ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝

EOF
    echo -e "${NC}"
}

# Print functions
print_step() {
    echo -e "\n${BOLD}${CYAN}[•]${NC} ${BOLD}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Detect Linux distribution
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
        VERSION_ID=$VERSION_ID
    elif [ -f /etc/redhat-release ]; then
        DISTRO="rhel"
    else
        DISTRO="unknown"
    fi
    
    print_success "Detected: $DISTRO $VERSION_ID"
}

# Check root privileges
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_warning "Not running as root. Some features may be limited."
        echo "Consider running: sudo $0"
        return 1
    fi
    return 0
}

# Check Python installation
check_python() {
    print_step "Checking Python installation..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        
        if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            print_success "Python $PYTHON_VERSION detected"
            return 0
        else
            print_error "Python 3.8+ required. Found: $PYTHON_VERSION"
            return 1
        fi
    else
        print_error "Python 3 not found"
        return 1
    fi
}

# Install Python if needed
install_python() {
    print_step "Installing Python 3..."
    
    case $DISTRO in
        ubuntu|debian)
            apt-get update
            apt-get install -y python3 python3-pip python3-venv
            ;;
        rhel|centos|fedora)
            yum install -y python3 python3-pip
            ;;
        arch)
            pacman -S --noconfirm python python-pip
            ;;
        *)
            print_error "Unsupported distribution: $DISTRO"
            return 1
            ;;
    esac
    
    print_success "Python installed"
}

# Install system dependencies
install_system_deps() {
    print_step "Installing system dependencies..."
    
    case $DISTRO in
        ubuntu|debian)
            apt-get update
            apt-get install -y git curl wget build-essential libssl-dev \
                libffi-dev python3-dev postgresql-client redis-tools
            ;;
        rhel|centos|fedora)
            yum install -y git curl wget gcc gcc-c++ make openssl-devel \
                libffi-devel python3-devel postgresql redis
            ;;
        arch)
            pacman -S --noconfirm git curl wget base-devel openssl \
                postgresql-libs redis
            ;;
    esac
    
    print_success "System dependencies installed"
}

# Create installation directory
create_install_dir() {
    print_step "Creating installation directory..."
    
    if [ -d "$INSTALL_DIR" ]; then
        print_warning "Installation directory already exists: $INSTALL_DIR"
    else
        mkdir -p "$INSTALL_DIR"
        print_success "Created: $INSTALL_DIR"
    fi
}

# Download platform files
download_platform() {
    print_step "Downloading CyberGuard platform..."
    
    cd /tmp
    
    if command -v git &> /dev/null; then
        git clone https://github.com/Amorleinis/recovery.git cyberguard-tmp
        cp -r cyberguard-tmp/* "$INSTALL_DIR/"
        rm -rf cyberguard-tmp
    else
        wget https://github.com/Amorleinis/recovery/archive/refs/heads/main.zip -O cyberguard.zip
        unzip -q cyberguard.zip
        cp -r recovery-main/* "$INSTALL_DIR/"
        rm -rf recovery-main cyberguard.zip
    fi
    
    print_success "Platform files downloaded"
}

# Create virtual environment
create_venv() {
    print_step "Creating virtual environment..."
    
    cd "$INSTALL_DIR"
    python3 -m venv .venv
    
    print_success "Virtual environment created"
}

# Install Python dependencies
install_dependencies() {
    local edition=$1
    print_step "Installing $edition dependencies..."
    
    cd "$INSTALL_DIR"
    source .venv/bin/activate
    
    pip install --upgrade pip
    
    case $edition in
        core)
            pip install -r requirements.txt
            ;;
        ml)
            pip install -r requirements.txt
            pip install -r requirements-ml.txt
            ;;
        performance)
            pip install -r requirements.txt
            pip install -r requirements-performance.txt
            ;;
        enterprise)
            pip install -r requirements.txt
            pip install -r requirements-ml.txt
            pip install -r requirements-performance.txt
            ;;
        dev)
            pip install -r requirements.txt
            pip install -r requirements-dev.txt
            ;;
    esac
    
    print_success "Dependencies installed"
    deactivate
}

# Create systemd service
create_systemd_service() {
    print_step "Creating systemd service..."
    
    cat > /etc/systemd/system/cyberguard-monitor.service << EOF
[Unit]
Description=CyberGuard Threat Monitor
After=network.target

[Service]
Type=simple
User=cyberguard
Group=cyberguard
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/.venv/bin"
ExecStart=$INSTALL_DIR/.venv/bin/python scripts/active_threat_monitor.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    cat > /etc/systemd/system/cyberguard-dashboard.service << EOF
[Unit]
Description=CyberGuard Web Dashboard
After=network.target

[Service]
Type=simple
User=cyberguard
Group=cyberguard
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/.venv/bin"
ExecStart=$INSTALL_DIR/.venv/bin/python scripts/threat_dashboard.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    cat > /etc/systemd/system/cyberguard-api.service << EOF
[Unit]
Description=CyberGuard API Server
After=network.target

[Service]
Type=simple
User=cyberguard
Group=cyberguard
WorkingDirectory=$INSTALL_DIR
Environment="PATH=$INSTALL_DIR/.venv/bin"
ExecStart=$INSTALL_DIR/.venv/bin/python scripts/api_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    print_success "Systemd services created"
}

# Create system user
create_user() {
    print_step "Creating system user..."
    
    if id "cyberguard" &>/dev/null; then
        print_warning "User 'cyberguard' already exists"
    else
        useradd -r -s /bin/false -d "$INSTALL_DIR" cyberguard
        print_success "User 'cyberguard' created"
    fi
    
    chown -R cyberguard:cyberguard "$INSTALL_DIR"
}

# Configure firewall
configure_firewall() {
    print_step "Configuring firewall..."
    
    if command -v ufw &> /dev/null; then
        ufw allow 5000/tcp comment 'CyberGuard Dashboard'
        ufw allow 8000/tcp comment 'CyberGuard API'
        ufw allow 9000/tcp comment 'CyberGuard Mobile API'
        print_success "UFW firewall configured"
    elif command -v firewall-cmd &> /dev/null; then
        firewall-cmd --permanent --add-port=5000/tcp
        firewall-cmd --permanent --add-port=8000/tcp
        firewall-cmd --permanent --add-port=9000/tcp
        firewall-cmd --reload
        print_success "Firewalld configured"
    else
        print_warning "No firewall detected"
    fi
}

# Create CLI symlink
create_cli_symlink() {
    print_step "Creating CLI command..."
    
    cat > /usr/local/bin/cyberguard << EOF
#!/bin/bash
cd $INSTALL_DIR
source .venv/bin/activate
python scripts/cli.py "\$@"
deactivate
EOF

    chmod +x /usr/local/bin/cyberguard
    print_success "CLI command 'cyberguard' created"
}

# Print next steps
show_next_steps() {
    echo ""
    echo -e "${CYAN}========================================================================${NC}"
    echo -e "${GREEN}${BOLD}✓ Installation Complete!${NC}"
    echo -e "${CYAN}========================================================================${NC}"
    echo ""
    echo -e "${BOLD}Next Steps:${NC}"
    echo ""
    echo -e "  ${CYAN}1. Start services:${NC}"
    echo -e "     ${BOLD}\$${NC} sudo systemctl start cyberguard-monitor"
    echo -e "     ${BOLD}\$${NC} sudo systemctl start cyberguard-dashboard"
    echo -e "     ${BOLD}\$${NC} sudo systemctl start cyberguard-api"
    echo ""
    echo -e "  ${CYAN}2. Enable services at boot:${NC}"
    echo -e "     ${BOLD}\$${NC} sudo systemctl enable cyberguard-monitor"
    echo -e "     ${BOLD}\$${NC} sudo systemctl enable cyberguard-dashboard"
    echo ""
    echo -e "  ${CYAN}3. Check status:${NC}"
    echo -e "     ${BOLD}\$${NC} cyberguard status"
    echo ""
    echo -e "  ${CYAN}4. Access web dashboard:${NC}"
    echo -e "     ${BOLD}http://localhost:5000${NC}"
    echo ""
    echo -e "  ${CYAN}5. View logs:${NC}"
    echo -e "     ${BOLD}\$${NC} sudo journalctl -u cyberguard-monitor -f"
    echo ""
    echo -e "${BOLD}Documentation:${NC}"
    echo -e "  📚 README: $INSTALL_DIR/README_ULTIMATE.md"
    echo -e "  📖 Docs: $INSTALL_DIR/docs/"
    echo -e "  🌐 Website: https://cyberguard-platform.com"
    echo ""
    echo -e "${CYAN}========================================================================${NC}"
    echo ""
}

# Main installation
main() {
    show_banner
    
    echo "Welcome to the CyberGuard Enterprise Platform installer!"
    echo "This will install CyberGuard to: $INSTALL_DIR"
    echo ""
    
    # Check for root
    IS_ROOT=0
    check_root && IS_ROOT=1
    
    # Detect distribution
    print_step "Detecting Linux distribution..."
    detect_distro
    
    # Prompt for edition
    echo ""
    echo -e "${BOLD}Select Edition:${NC}"
    echo "  1. Core (Free - Basic features)"
    echo "  2. Professional (ML + Analytics)"
    echo "  3. Enterprise (Full features)"
    echo "  4. Development (All features + dev tools)"
    echo ""
    read -p "Enter choice [1-4] (default: 1): " choice
    choice=${choice:-1}
    
    case $choice in
        1) EDITION="core" ;;
        2) EDITION="ml" ;;
        3) EDITION="enterprise" ;;
        4) EDITION="dev" ;;
        *) EDITION="core" ;;
    esac
    
    echo ""
    echo -e "${GREEN}Installing ${EDITION^^} Edition...${NC}"
    echo ""
    
    # Check Python
    if ! check_python; then
        if [ $IS_ROOT -eq 1 ]; then
            install_python
        else
            print_error "Please install Python 3.8+ or run with sudo"
            exit 1
        fi
    fi
    
    # Install system dependencies
    if [ $IS_ROOT -eq 1 ]; then
        install_system_deps
    fi
    
    # Create installation directory
    create_install_dir
    
    # Download platform
    download_platform
    
    # Create virtual environment
    create_venv
    
    # Install dependencies
    install_dependencies "$EDITION"
    
    # Root-only configurations
    if [ $IS_ROOT -eq 1 ]; then
        create_user
        create_systemd_service
        configure_firewall
        create_cli_symlink
    fi
    
    show_next_steps
}

# Run installer
main "$@"
