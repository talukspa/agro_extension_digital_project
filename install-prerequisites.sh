#!/bin/bash

# Script to install all prerequisites for Agro Extension Digital Project
# Run with: bash install-prerequisites.sh

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function for colored output
print_message() {
    echo -e "${1}${2}${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Homebrew if not present
install_homebrew() {
    print_message $YELLOW "🔧 Checking for Homebrew..."
    if command_exists brew; then
        print_message $GREEN "✅ Homebrew already installed: $(brew --version | head -n1)"
    else
        print_message $YELLOW "📦 Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

        # Add Homebrew to PATH for ARM Macs
        if [[ "$(uname -m)" == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi

        print_message $GREEN "✅ Homebrew installed successfully"
    fi
}

# Function to install a tool with Homebrew
install_with_brew() {
    local tool=$1
    local package_name=${2:-$tool}

    print_message $YELLOW "🔧 Checking for $tool..."
    if command_exists "$tool"; then
        local version=""
        case $tool in
            gcloud)
                version=$(gcloud --version 2>/dev/null | head -n1 || echo "unknown")
                ;;
            terraform)
                version=$(terraform --version 2>/dev/null | head -n1 || echo "unknown")
                ;;
            terragrunt)
                version=$(terragrunt --version 2>/dev/null | head -n1 || echo "unknown")
                ;;
            node)
                version=$(node --version 2>/dev/null || echo "unknown")
                ;;
            pnpm)
                version=$(pnpm --version 2>/dev/null || echo "unknown")
                ;;
            python3)
                version=$(python3 --version 2>/dev/null || echo "unknown")
                ;;
            uv)
                version=$(uv --version 2>/dev/null || echo "unknown")
                ;;
            *)
                version="installed"
                ;;
        esac
        print_message $GREEN "✅ $tool already installed ($version)"
    else
        print_message $YELLOW "📦 Installing $tool..."
        brew install "$package_name"
        print_message $GREEN "✅ $tool installed"
    fi
}

# Function to configure Google Cloud SDK
configure_gcloud() {
    print_message $YELLOW "☁️ Configuring Google Cloud SDK..."

    # Check if gcloud is authenticated
    if gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | grep -q .; then
        local account=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" 2>/dev/null | head -n1)
        print_message $GREEN "✅ Google Cloud already authenticated as: $account"
    else
        print_message $YELLOW "🔐 Google Cloud authentication required"
        echo ""
        print_message $BLUE "Please follow these steps:"
        echo "1. A browser window will open for Google authentication"
        echo "2. Log in with your Google account"
        echo "3. Allow the requested permissions"
        echo ""
        read -p "Press Enter to continue with gcloud auth login..."
        gcloud auth login

        print_message $YELLOW "🔐 Setting up application default credentials..."
        gcloud auth application-default login

        print_message $GREEN "✅ Google Cloud authentication completed"
    fi

    # Check current project
    local current_project=$(gcloud config get-value project 2>/dev/null || echo "")
    if [[ -n "$current_project" ]]; then
        print_message $GREEN "✅ Current Google Cloud project: $current_project"
    else
        print_message $YELLOW "⚠️ No Google Cloud project configured"
        print_message $BLUE "You can set a project later with: gcloud config set project PROJECT_ID"
    fi
}

# Function to verify all installations
verify_installations() {
    print_message $BLUE "🔍 Verifying all installations..."
    echo ""

    local tools=(
        "brew:Homebrew"
        "gcloud:Google Cloud SDK"
        "terraform:Terraform"
        "terragrunt:Terragrunt"
        "node:Node.js"
        "pnpm:pnpm"
        "python3:Python 3"
        "uv:UV (Python package manager)"
        "docker:Docker"
    )

    local all_ok=true

    for tool_entry in "${tools[@]}"; do
        IFS=':' read -r tool_name tool_desc <<< "$tool_entry"

        if command_exists "$tool_name"; then
            print_message $GREEN "✅ $tool_desc is installed"
        else
            print_message $RED "❌ $tool_desc is NOT installed"
            all_ok=false
        fi
    done

    echo ""
    if $all_ok; then
        print_message $GREEN "🎉 All prerequisites installed successfully!"
    else
        print_message $RED "⚠️ Some tools are missing. Please check the installation."
        exit 1
    fi
}

# Function to show next steps
show_next_steps() {
    print_message $BLUE "📋 NEXT STEPS FOR DEPLOYMENT:"
    echo ""
    echo "1. Create Terraform state buckets (required once):"
    echo "   bash scripts/create-tf-state-buckets.sh"
    echo ""
    echo "2. Configure GitHub Actions self-hosted runner:"
    echo "   - Go to GitHub → Settings → Actions → Runners"
    echo "   - Click 'New self-hosted runner'"
    echo "   - Follow instructions to configure runner"
    echo ""
    echo "3. Set up secrets (Firebase & WhatsApp):"
    echo "   bash scripts/setup-secrets.sh"
    echo ""
    echo "4. Validate system:"
    echo "   bash scripts/pre-execution-validation.sh"
    echo ""
    echo "5. Deploy development environment:"
    echo "   bash scripts/deploy-complete.sh dev"
    echo ""
    print_message $YELLOW "📚 Documentation available in docs/frontend/"
}

# Main installation function
main() {
    echo -e "${BLUE}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║             📦 PREREQUISITES INSTALLATION SCRIPT              ║
║                 Agro Extension Digital Project                ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    # Check OS
    if [[ "$(uname)" != "Darwin" ]]; then
        print_message $RED "❌ This script is designed for macOS"
        print_message $RED "   Detected OS: $(uname)"
        exit 1
    fi

    print_message $YELLOW "🖥️  System: $(uname -m) macOS $(sw_vers -productVersion)"
    echo ""

    # Install Homebrew first
    install_homebrew

    # Update Homebrew
    print_message $YELLOW "🔄 Updating Homebrew..."
    brew update
    print_message $GREEN "✅ Homebrew updated"
    echo ""

    # Install all tools
    print_message $BLUE "🚀 Installing required tools..."
    echo ""

    install_with_brew "gcloud" "google-cloud-sdk"
    install_with_brew "terraform"
    install_with_brew "terragrunt"
    install_with_brew "node"
    install_with_brew "pnpm"
    install_with_brew "python3" "python@3.12"
    install_with_brew "uv"

    # Note about Docker
    print_message $YELLOW "🐳 Checking Docker..."
    if command_exists docker; then
        print_message $GREEN "✅ Docker already installed: $(docker --version | head -n1)"
    else
        print_message $YELLOW "📦 Docker needs to be installed separately"
        print_message $BLUE "   Download from: https://docs.docker.com/desktop/"
        print_message $BLUE "   Or install with: brew install --cask docker"
    fi

    echo ""

    # Configure Google Cloud
    configure_gcloud

    echo ""

    # Verify installations
    verify_installations

    echo ""

    # Show next steps
    show_next_steps
}

# Run main function
main "$@"