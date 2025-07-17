#!/usr/bin/env python3
"""
# this_file: scripts/test.py
Test script for dimjournal project
"""
import subprocess
import sys
import logging
from pathlib import Path
import os

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def run_command(cmd, check=True, cwd=None):
    """Run a command and return the result."""
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, cwd=cwd, capture_output=True, text=True)
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    return result

def install_test_dependencies():
    """Install testing dependencies."""
    logger.info("Installing testing dependencies...")
    run_command([sys.executable, "-m", "pip", "install", "-e", ".[testing]"])
    run_command([sys.executable, "-m", "pip", "install", "flake8", "black", "isort"])

def run_linting():
    """Run code linting."""
    logger.info("Running linting...")
    
    # Run flake8
    logger.info("Running flake8...")
    run_command(["flake8", "src", "tests", "scripts"])
    
    # Run black check
    logger.info("Running black check...")
    run_command(["black", "--check", "src", "tests", "scripts"])
    
    # Run isort check
    logger.info("Running isort check...")
    run_command(["isort", "--check-only", "src", "tests", "scripts"])

def run_tests():
    """Run the test suite."""
    logger.info("Running tests...")
    
    # Run pytest with coverage
    run_command([
        sys.executable, "-m", "pytest",
        "--verbose",
        "--cov=dimjournal",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-report=xml",
        "tests/"
    ])

def format_code():
    """Format code using black and isort."""
    logger.info("Formatting code...")
    
    # Run black
    logger.info("Running black formatter...")
    run_command(["black", "src", "tests", "scripts"])
    
    # Run isort
    logger.info("Running isort...")
    run_command(["isort", "src", "tests", "scripts"])

def main():
    """Main test function."""
    logger.info("Starting test process...")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        install_test_dependencies()
        
        # Check if format flag is passed
        if len(sys.argv) > 1 and sys.argv[1] == "--format":
            format_code()
            return
        
        # Check if lint-only flag is passed
        if len(sys.argv) > 1 and sys.argv[1] == "--lint-only":
            run_linting()
            return
        
        # Run full test suite
        run_linting()
        run_tests()
        
        logger.info("All tests passed successfully!")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Tests failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()