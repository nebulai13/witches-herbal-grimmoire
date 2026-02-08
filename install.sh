#!/usr/bin/env bash
#
# Grimmoire Installation Script
# Traditional Medicine & Ingredients Search REPL
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="${HOME}/.grimmoire"
VENV_DIR="${INSTALL_DIR}/venv"
BIN_LINK="/usr/local/bin/grimmoire"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                                                               ║"
    echo "║   🌿  GRIMMOIRE INSTALLER  🌿                                 ║"
    echo "║   Traditional Medicine & Ingredients Search                   ║"
    echo "║                                                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_python() {
    log_info "Checking Python version..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python not found. Please install Python 3.9 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
    PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
    PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')
    
    if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 9 ]]; then
        log_error "Python 3.9+ required. Found: $PYTHON_VERSION"
        exit 1
    fi
    
    log_success "Python $PYTHON_VERSION found"
}

check_pip() {
    log_info "Checking pip..."
    
    if ! $PYTHON_CMD -m pip --version &> /dev/null; then
        log_error "pip not found. Please install pip."
        exit 1
    fi
    
    log_success "pip found"
}

create_venv() {
    log_info "Creating virtual environment at $VENV_DIR..."
    
    mkdir -p "$INSTALL_DIR"
    
    if [[ -d "$VENV_DIR" ]]; then
        log_warn "Virtual environment already exists. Removing..."
        rm -rf "$VENV_DIR"
    fi
    
    $PYTHON_CMD -m venv "$VENV_DIR"
    log_success "Virtual environment created"
}

install_package() {
    log_info "Installing Grimmoire and dependencies..."
    
    source "$VENV_DIR/bin/activate"
    
    # Upgrade pip
    pip install --upgrade pip --quiet
    
    # Install the package
    pip install -e "$SCRIPT_DIR" --quiet
    
    deactivate
    
    log_success "Grimmoire installed"
}

create_launcher() {
    log_info "Creating launcher script..."
    
    LAUNCHER="${INSTALL_DIR}/grimmoire"
    
    cat > "$LAUNCHER" << 'EOF'
#!/usr/bin/env bash
# Grimmoire Launcher
INSTALL_DIR="${HOME}/.grimmoire"
source "${INSTALL_DIR}/venv/bin/activate"
python -m grimmoire.main "$@"
deactivate
EOF
    
    chmod +x "$LAUNCHER"
    log_success "Launcher created at $LAUNCHER"
    
    # Try to create symlink in /usr/local/bin
    if [[ -w "/usr/local/bin" ]]; then
        ln -sf "$LAUNCHER" "$BIN_LINK" 2>/dev/null && \
            log_success "Symlink created at $BIN_LINK" || \
            log_warn "Could not create symlink at $BIN_LINK"
    else
        log_warn "Cannot write to /usr/local/bin. You may need to run:"
        echo "    sudo ln -sf $LAUNCHER $BIN_LINK"
    fi
}

create_alias_instructions() {
    echo ""
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}Installation Complete!${NC}"
    echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "To run Grimmoire:"
    echo ""
    echo "  1. Direct: ${INSTALL_DIR}/grimmoire"
    echo ""
    echo "  2. Add to your shell profile (~/.bashrc or ~/.zshrc):"
    echo "     alias grimmoire='${INSTALL_DIR}/grimmoire'"
    echo ""
    echo "  3. Or if symlink was created: grimmoire"
    echo ""
    echo "Getting Started:"
    echo "  grimmoire                     # Start the REPL"
    echo "  grimmoire --help              # Show help"
    echo ""
    echo "First time? Run these commands in the REPL:"
    echo "  scrape \"NAEB Datasette\"       # Load ethnobotany data"
    echo "  search plant chamomile        # Search for plants"
    echo "  pubmed turmeric               # Search PubMed"
    echo ""
    echo "Documentation: ${SCRIPT_DIR}/docs/"
    echo ""
}

install_dev() {
    log_info "Installing in development mode (current directory)..."
    
    check_python
    check_pip
    
    $PYTHON_CMD -m pip install -e "$SCRIPT_DIR"
    
    log_success "Development installation complete"
    echo ""
    echo "Run with: python -m grimmoire.main"
}

uninstall() {
    log_info "Uninstalling Grimmoire..."
    
    if [[ -d "$INSTALL_DIR" ]]; then
        rm -rf "$INSTALL_DIR"
        log_success "Removed $INSTALL_DIR"
    fi
    
    if [[ -L "$BIN_LINK" ]]; then
        rm -f "$BIN_LINK" 2>/dev/null && \
            log_success "Removed $BIN_LINK" || \
            log_warn "Could not remove $BIN_LINK (may need sudo)"
    fi
    
    log_success "Uninstallation complete"
}

show_help() {
    echo "Grimmoire Installation Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install     Install Grimmoire to ~/.grimmoire (default)"
    echo "  dev         Install in development mode (no venv)"
    echo "  uninstall   Remove Grimmoire installation"
    echo "  help        Show this help message"
    echo ""
}

# Main
main() {
    local command="${1:-install}"
    
    case "$command" in
        install)
            print_banner
            check_python
            check_pip
            create_venv
            install_package
            create_launcher
            create_alias_instructions
            ;;
        dev)
            print_banner
            install_dev
            ;;
        uninstall)
            uninstall
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
