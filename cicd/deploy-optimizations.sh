#!/bin/bash

# Cloud Run Performance Optimization Deployment Script
# This script validates and applies the performance optimizations to Cloud Run services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required tools are installed
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    if ! command -v terragrunt &> /dev/null; then
        print_error "Terragrunt is not installed. Please install terragrunt first."
        exit 1
    fi
    
    if ! command -v terraform &> /dev/null; then
        print_error "Terraform is not installed. Please install terraform first."
        exit 1
    fi
    
    if ! command -v gcloud &> /dev/null; then
        print_error "Google Cloud CLI is not installed. Please install gcloud first."
        exit 1
    fi
    
    print_success "All prerequisites are installed."
}

# Function to validate Terraform configuration
validate_terraform() {
    local env=$1
    print_status "Validating Terraform configuration for $env environment..."
    
    cd "cicd/$env"
    
    # Initialize and validate
    if terragrunt init; then
        print_success "Terragrunt initialization successful for $env"
    else
        print_error "Terragrunt initialization failed for $env"
        return 1
    fi
    
    if terragrunt validate; then
        print_success "Terraform validation successful for $env"
    else
        print_error "Terraform validation failed for $env"
        return 1
    fi
    
    # Plan the changes
    if terragrunt plan -out="tfplan-$env"; then
        print_success "Terraform plan successful for $env"
    else
        print_error "Terraform plan failed for $env"
        return 1
    fi
    
    cd "../.."
}

# Function to show the planned changes
show_plan() {
    local env=$1
    print_status "Showing planned changes for $env environment..."
    
    cd "cicd/$env"
    terragrunt show "tfplan-$env"
    cd "../.."
}

# Function to apply changes
apply_changes() {
    local env=$1
    print_status "Applying changes for $env environment..."
    
    cd "cicd/$env"
    
    if terragrunt apply "tfplan-$env"; then
        print_success "Changes applied successfully for $env"
    else
        print_error "Failed to apply changes for $env"
        return 1
    fi
    
    cd "../.."
}

# Function to check Cloud Run service status
check_service_status() {
    local env=$1
    local project_id=$2
    local region="us-central1"
    
    print_status "Checking Cloud Run service status for $env environment..."
    
    # Set the project
    gcloud config set project "$project_id"
    
    # Check agent-aa service
    local agent_aa_service="agent-aa-$env"
    if [[ "$env" == "dev" ]]; then
        agent_aa_service="agent-dev"
    fi
    
    print_status "Checking service: $agent_aa_service"
    if gcloud run services describe "$agent_aa_service" --region="$region" --format="value(status.url)" &> /dev/null; then
        local agent_url=$(gcloud run services describe "$agent_aa_service" --region="$region" --format="value(status.url)")
        print_success "Agent AA service is running: $agent_url"
    else
        print_warning "Agent AA service status could not be determined"
    fi
    
    # Check webhook service
    local webhook_service="agent-webhook-$env"
    print_status "Checking service: $webhook_service"
    if gcloud run services describe "$webhook_service" --region="$region" --format="value(status.url)" &> /dev/null; then
        local webhook_url=$(gcloud run services describe "$webhook_service" --region="$region" --format="value(status.url)")
        print_success "Webhook service is running: $webhook_url"
    else
        print_warning "Webhook service status could not be determined"
    fi
}

# Main function
main() {
    print_status "Starting Cloud Run Performance Optimization Deployment"
    print_status "======================================================="
    
    # Check if we're in the right directory
    if [[ ! -d "cicd" ]]; then
        print_error "Please run this script from the project root directory"
        exit 1
    fi
    
    # Check prerequisites
    check_prerequisites
    
    # Get environment from command line argument
    local environment=${1:-""}
    
    if [[ -z "$environment" ]]; then
        print_status "Available environments:"
        print_status "  dev - Development environment"
        print_status "  prd - Production environment"
        print_status "  all - Both environments"
        echo
        read -p "Please select an environment (dev/prd/all): " environment
    fi
    
    case $environment in
        "dev")
            print_status "Processing development environment..."
            validate_terraform "dev"
            show_plan "dev"
            read -p "Do you want to apply these changes to the development environment? (y/N): " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                apply_changes "dev"
                check_service_status "dev" "agro-extension-digital-npe"
            else
                print_warning "Skipping deployment to development environment"
            fi
            ;;
        "prd")
            print_status "Processing production environment..."
            validate_terraform "prd"
            show_plan "prd"
            print_warning "You are about to modify the PRODUCTION environment!"
            read -p "Are you sure you want to apply these changes to production? (y/N): " confirm
            if [[ $confirm =~ ^[Yy]$ ]]; then
                apply_changes "prd"
                check_service_status "prd" "agro-extension-digital-prd"
            else
                print_warning "Skipping deployment to production environment"
            fi
            ;;
        "all")
            print_status "Processing both environments..."
            
            # Development first
            validate_terraform "dev"
            show_plan "dev"
            read -p "Do you want to apply these changes to the development environment? (y/N): " confirm_dev
            if [[ $confirm_dev =~ ^[Yy]$ ]]; then
                apply_changes "dev"
                check_service_status "dev" "agro-extension-digital-npe"
            fi
            
            # Production second
            validate_terraform "prd"
            show_plan "prd"
            print_warning "You are about to modify the PRODUCTION environment!"
            read -p "Are you sure you want to apply these changes to production? (y/N): " confirm_prd
            if [[ $confirm_prd =~ ^[Yy]$ ]]; then
                apply_changes "prd"
                check_service_status "prd" "agro-extension-digital-prd"
            fi
            ;;
        *)
            print_error "Invalid environment: $environment"
            print_status "Valid options are: dev, prd, all"
            exit 1
            ;;
    esac
    
    print_success "Deployment script completed!"
    print_status "======================================================="
    print_status "Next steps:"
    print_status "1. Monitor the services using Google Cloud Console"
    print_status "2. Review performance metrics in Cloud Monitoring"
    print_status "3. Conduct load testing to validate optimizations"
    print_status "4. Check the PERFORMANCE_OPTIMIZATIONS.md file for details"
}

# Run the main function with all arguments
main "$@"
