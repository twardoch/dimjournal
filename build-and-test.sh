#!/bin/bash
# this_file: build-and-test.sh
# Convenient build and test script for dimjournal

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Default values
ACTION="all"
BINARY=false
FORMAT=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "OPTIONS:"
            echo "  -h, --help     Show this help message"
            echo "  -t, --test     Run tests only"
            echo "  -b, --build    Build package only"
            echo "  -r, --release  Build and release (requires version)"
            echo "  --binary       Build binary along with package"
            echo "  --format       Format code before running tests"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run all tests and build"
            echo "  $0 --test             # Run tests only"
            echo "  $0 --build --binary   # Build package and binary"
            echo "  $0 --release v1.0.0   # Release version 1.0.0"
            echo "  $0 --format --test    # Format code and run tests"
            exit 0
            ;;
        -t|--test)
            ACTION="test"
            shift
            ;;
        -b|--build)
            ACTION="build"
            shift
            ;;
        -r|--release)
            ACTION="release"
            VERSION="$2"
            shift 2
            ;;
        --binary)
            BINARY=true
            shift
            ;;
        --format)
            FORMAT=true
            shift
            ;;
        *)
            log_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Check if we're in the project root
if [ ! -f "pyproject.toml" ] || [ ! -f "setup.cfg" ]; then
    log_error "This script must be run from the project root directory"
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null; then
    log_error "Python is not installed or not in PATH"
    exit 1
fi

# Check if scripts directory exists
if [ ! -d "scripts" ]; then
    log_error "Scripts directory not found"
    exit 1
fi

# Format code if requested
if [ "$FORMAT" = true ]; then
    log_info "Formatting code..."
    python scripts/test.py --format
fi

# Execute based on action
case $ACTION in
    "test")
        log_info "Running tests..."
        python scripts/test.py
        ;;
    "build")
        log_info "Building package..."
        if [ "$BINARY" = true ]; then
            python scripts/build.py --binary
        else
            python scripts/build.py
        fi
        ;;
    "release")
        if [ -z "$VERSION" ]; then
            log_error "Version required for release. Use: $0 --release v1.0.0"
            exit 1
        fi
        log_info "Releasing version $VERSION..."
        python scripts/release.py "$VERSION"
        ;;
    "all")
        log_info "Running full build and test pipeline..."
        
        # Run tests first
        log_info "Step 1: Running tests..."
        python scripts/test.py
        
        # Build package
        log_info "Step 2: Building package..."
        if [ "$BINARY" = true ]; then
            python scripts/build.py --binary
        else
            python scripts/build.py
        fi
        
        log_info "Build and test completed successfully!"
        ;;
    *)
        log_error "Unknown action: $ACTION"
        exit 1
        ;;
esac

log_info "Script completed successfully!"