#!/bin/bash

# Autonomous SDLC Setup Script
# This script sets up the environment and validates the installation

set -e  # Exit on error

echo "=========================================="
echo "Autonomous SDLC - Setup Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo "ℹ $1"
}

# Check Python version
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PIP_CMD=pip3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    PIP_CMD=pip
else
    print_error "Python is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION found"

# Check Python version is 3.8+
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required. You have Python $PYTHON_VERSION"
    exit 1
fi

print_success "Python version is compatible"

# Check pip
echo ""
echo "Checking pip installation..."
if command -v $PIP_CMD &> /dev/null; then
    PIP_VERSION=$($PIP_CMD --version 2>&1 | awk '{print $2}')
    print_success "pip $PIP_VERSION found"
else
    print_error "pip is not installed. Please install pip."
    exit 1
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
print_info "This may take a minute..."

if $PIP_CMD install -r requirements.txt --quiet; then
    print_success "Dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi

# Check for Anthropic package
echo ""
echo "Verifying Anthropic SDK..."
if $PYTHON_CMD -c "import anthropic" 2>/dev/null; then
    print_success "Anthropic SDK installed"
else
    print_error "Anthropic SDK not found. Installing..."
    $PIP_CMD install anthropic
fi

# Create .env file if it doesn't exist
echo ""
if [ -f .env ]; then
    print_warning ".env file already exists. Skipping..."
else
    print_info "Creating .env file from template..."
    cp .env.example .env
    print_success ".env file created"
    print_warning "⚠ IMPORTANT: Edit .env and add your ANTHROPIC_API_KEY"
fi

# Check for API key
echo ""
if [ -z "$ANTHROPIC_API_KEY" ] && ! grep -q "ANTHROPIC_API_KEY=sk-" .env 2>/dev/null; then
    print_warning "Anthropic API key not configured"
    echo ""
    echo "To set your API key:"
    echo "  1. Get your key from: https://console.anthropic.com/"
    echo "  2. Run: export ANTHROPIC_API_KEY='your-key-here'"
    echo "  OR edit .env file and add your key"
else
    print_success "API key configured"
fi

# Create output directory
echo ""
if [ ! -d "output" ]; then
    mkdir -p output
    print_success "Output directory created"
else
    print_info "Output directory already exists"
fi

# Run a simple test
echo ""
echo "Running validation test..."
if $PYTHON_CMD -c "
import sys
sys.path.insert(0, '.')
from config.settings import Config
try:
    config = Config()
    print('OK')
except ValueError as e:
    if 'ANTHROPIC_API_KEY' in str(e):
        print('API_KEY_MISSING')
    else:
        print('ERROR')
" 2>/dev/null | grep -q "OK\|API_KEY_MISSING"; then
    print_success "System validated successfully"
else
    print_error "System validation failed"
    exit 1
fi

# Summary
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
print_success "Python dependencies installed"
print_success "Environment configured"
print_success "System validated"
echo ""
echo "Next Steps:"
echo "  1. Set your API key (if not done):"
echo "     export ANTHROPIC_API_KEY='sk-ant-your-key'"
echo ""
echo "  2. Run the example:"
echo "     $PYTHON_CMD main.py example_requirements.md"
echo ""
echo "  3. Or create your own requirements.md and run:"
echo "     $PYTHON_CMD main.py your_requirements.md"
echo ""
echo "For help, see README.md or QUICKSTART.md"
echo ""
print_success "Ready to build! 🚀"
