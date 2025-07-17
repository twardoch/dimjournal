#!/usr/bin/env python3
"""
# this_file: scripts/release.py
Release script for dimjournal project
"""
import subprocess
import sys
import logging
from pathlib import Path
import os
import re
from datetime import datetime

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

def get_current_version():
    """Get current version from git tags."""
    try:
        result = run_command(["git", "describe", "--tags", "--abbrev=0"], check=False)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return "v0.0.0"
    except:
        return "v0.0.0"

def validate_version(version):
    """Validate version format."""
    pattern = r'^v?\d+\.\d+\.\d+$'
    return re.match(pattern, version) is not None

def check_working_directory():
    """Check if working directory is clean."""
    result = run_command(["git", "status", "--porcelain"], check=False)
    if result.stdout.strip():
        logger.error("Working directory is not clean. Please commit or stash changes.")
        return False
    return True

def run_tests():
    """Run the test suite."""
    logger.info("Running tests before release...")
    run_command([sys.executable, "scripts/test.py"])

def build_package():
    """Build the package."""
    logger.info("Building package...")
    run_command([sys.executable, "scripts/build.py"])

def create_git_tag(version):
    """Create and push git tag."""
    logger.info(f"Creating git tag: {version}")
    
    # Create tag
    run_command(["git", "tag", "-a", version, "-m", f"Release {version}"])
    
    # Push tag
    run_command(["git", "push", "origin", version])

def update_changelog(version):
    """Update changelog with new version."""
    changelog_path = Path("CHANGELOG.md")
    
    if not changelog_path.exists():
        logger.warning("CHANGELOG.md not found, skipping changelog update")
        return
    
    # Read current changelog
    with open(changelog_path, 'r') as f:
        content = f.read()
    
    # Find [Unreleased] section
    today = datetime.now().strftime('%Y-%m-%d')
    unreleased_pattern = r'## \[Unreleased\]'
    new_section = f'## [Unreleased]\\n\\n## [{version.lstrip("v")}] - {today}'
    
    # Replace [Unreleased] with new version
    updated_content = re.sub(unreleased_pattern, new_section, content)
    
    # Write back to file
    with open(changelog_path, 'w') as f:
        f.write(updated_content)
    
    logger.info(f"Updated CHANGELOG.md with version {version}")

def main():
    """Main release function."""
    if len(sys.argv) != 2:
        logger.error("Usage: python scripts/release.py <version>")
        logger.error("Example: python scripts/release.py v1.0.0")
        sys.exit(1)
    
    version = sys.argv[1]
    
    # Validate version format
    if not validate_version(version):
        logger.error(f"Invalid version format: {version}")
        logger.error("Version should be in format: v1.0.0")
        sys.exit(1)
    
    # Ensure version starts with 'v'
    if not version.startswith('v'):
        version = f'v{version}'
    
    logger.info(f"Starting release process for version: {version}")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    try:
        # Check working directory
        if not check_working_directory():
            sys.exit(1)
        
        # Check if tag already exists
        result = run_command(["git", "tag", "-l", version], check=False)
        if result.stdout.strip():
            logger.error(f"Tag {version} already exists!")
            sys.exit(1)
        
        # Run tests
        run_tests()
        
        # Update changelog
        update_changelog(version)
        
        # Build package
        build_package()
        
        # Create git tag
        create_git_tag(version)
        
        logger.info(f"Release {version} completed successfully!")
        logger.info("GitHub Actions will automatically build and publish the package.")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Release failed: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()