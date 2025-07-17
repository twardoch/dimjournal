#!/usr/bin/env python3
"""
# this_file: scripts/build.py
Build script for dimjournal project
"""
import subprocess
import sys
import logging
from pathlib import Path
import shutil

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

def clean_build():
    """Clean previous build artifacts."""
    logger.info("Cleaning previous build artifacts...")
    
    # Remove build directories
    dirs_to_remove = ['build', 'dist', 'src/dimjournal.egg-info']
    for dir_path in dirs_to_remove:
        if Path(dir_path).exists():
            shutil.rmtree(dir_path)
            logger.info(f"Removed {dir_path}")
    
    # Remove compiled Python files
    for pattern in ['**/*.pyc', '**/*.pyo', '**/__pycache__']:
        for path in Path('.').glob(pattern):
            if path.is_file():
                path.unlink()
                logger.info(f"Removed {path}")
            elif path.is_dir():
                shutil.rmtree(path)
                logger.info(f"Removed {path}")

def install_dependencies():
    """Install build dependencies."""
    logger.info("Installing build dependencies...")
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "build", "setuptools", "setuptools_scm", "wheel"])

def build_package():
    """Build the package."""
    logger.info("Building package...")
    run_command([sys.executable, "-m", "build"])

def build_binary():
    """Build standalone binary using PyInstaller."""
    logger.info("Building standalone binary...")
    
    # Install PyInstaller if not present
    try:
        import PyInstaller
    except ImportError:
        logger.info("Installing PyInstaller...")
        run_command([sys.executable, "-m", "pip", "install", "PyInstaller"])
    
    # Create binary
    run_command([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "dimjournal",
        "--hidden-import", "dimjournal",
        "--hidden-import", "undetected_chromedriver",
        "--hidden-import", "selenium",
        "--hidden-import", "PIL",
        "--hidden-import", "pymtpng",
        "src/dimjournal/__main__.py"
    ])

def main():
    """Main build function."""
    logger.info("Starting build process...")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        clean_build()
        install_dependencies()
        build_package()
        
        # Build binary if requested
        if len(sys.argv) > 1 and sys.argv[1] == "--binary":
            build_binary()
        
        logger.info("Build completed successfully!")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Build failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import os
    main()