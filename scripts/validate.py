#!/usr/bin/env python3
"""
# this_file: scripts/validate.py
Validation script for dimjournal project (without dependencies)
"""
import sys
import os
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists and report."""
    if Path(file_path).exists():
        print(f"✓ {description}: {file_path}")
        return True
    else:
        print(f"✗ {description}: {file_path} (missing)")
        return False

def check_python_syntax(file_path):
    """Check Python syntax of a file."""
    try:
        with open(file_path, 'r') as f:
            compile(f.read(), file_path, 'exec')
        print(f"✓ Python syntax valid: {file_path}")
        return True
    except SyntaxError as e:
        print(f"✗ Python syntax error in {file_path}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error checking {file_path}: {e}")
        return False

def main():
    """Main validation function."""
    print("=== Dimjournal Project Validation ===\n")
    
    # Change to project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    all_good = True
    
    # Check core files
    print("1. Core Files:")
    core_files = [
        ("pyproject.toml", "Build configuration"),
        ("setup.cfg", "Package metadata"),
        ("README.md", "Documentation"),
        ("CHANGELOG.md", "Change history"),
        ("LICENSE.txt", "License"),
        (".github/workflows/ci.yml", "CI/CD workflow"),
        ("Makefile", "Build automation"),
        ("build-and-test.sh", "Build script")
    ]
    
    for file_path, description in core_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    print("\n2. Source Code:")
    source_files = [
        "src/dimjournal/__init__.py",
        "src/dimjournal/__main__.py", 
        "src/dimjournal/dimjournal.py"
    ]
    
    for file_path in source_files:
        if check_file_exists(file_path, "Source file"):
            if not check_python_syntax(file_path):
                all_good = False
        else:
            all_good = False
    
    print("\n3. Test Files:")
    test_files = [
        "tests/test_dimjournal.py",
        "tests/conftest.py"
    ]
    
    for file_path in test_files:
        if Path(file_path).exists():
            if not check_python_syntax(file_path):
                all_good = False
    
    print("\n4. Scripts:")
    script_files = [
        "scripts/build.py",
        "scripts/test.py",
        "scripts/release.py",
        "scripts/validate.py"
    ]
    
    for file_path in script_files:
        if check_file_exists(file_path, "Script file"):
            if not check_python_syntax(file_path):
                all_good = False
        else:
            all_good = False
    
    print("\n5. Git Configuration:")
    try:
        result = subprocess.run(["git", "status"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ Git repository initialized")
        else:
            print("✗ Git repository not initialized")
            all_good = False
    except FileNotFoundError:
        print("✗ Git not found")
        all_good = False
    
    print("\n=== Validation Summary ===")
    if all_good:
        print("✓ All validations passed!")
        print("\nNext steps:")
        print("1. Set up a Python virtual environment:")
        print("   python3 -m venv venv")
        print("   source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
        print("2. Install dependencies:")
        print("   pip install -e .[dev]")
        print("3. Run tests:")
        print("   python scripts/test.py")
        print("4. Build package:")
        print("   python scripts/build.py")
        print("5. Create release:")
        print("   python scripts/release.py v1.0.0")
    else:
        print("✗ Some validations failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()