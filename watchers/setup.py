"""
Setup script for AI Employee Watchers.
Cross-platform: works on Windows, macOS, Linux.

Usage:
    python setup.py          # Install dependencies
    python setup.py --test   # Install and run basic validation
"""

import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Ensure Python 3.13+ is installed."""
    if sys.version_info < (3, 13):
        print(f"ERROR: Python 3.13+ required. You have {sys.version}")
        print("Download from: https://www.python.org/downloads/")
        sys.exit(1)
    print(f"Python {sys.version.split()[0]} - OK")


def install_dependencies():
    """Install required Python packages."""
    print("\nInstalling dependencies...")
    
    requirements = Path(__file__).parent / "requirements.txt"
    if not requirements.exists():
        print("ERROR: requirements.txt not found")
        sys.exit(1)
    
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e}")
        sys.exit(1)


def test_imports():
    """Verify all modules import correctly."""
    print("\nTesting module imports...")
    
    tests = [
        ("base_watcher", "BaseWatcher"),
        ("filesystem_watcher", "FileSystemWatcher"),
        ("orchestrator", "Orchestrator"),
    ]
    
    all_passed = True
    for module, class_name in tests:
        try:
            mod = __import__(module)
            cls = getattr(mod, class_name)
            print(f"  {module}.{class_name} - OK")
        except ImportError as e:
            print(f"  {module}.{class_name} - FAILED: {e}")
            all_passed = False
    
    return all_passed


def test_vault_structure():
    """Verify the vault folder structure exists."""
    print("\nTesting vault structure...")
    
    vault_path = Path(__file__).parent.parent / "AI_Employee_Vault"
    required_dirs = [
        "Inbox",
        "Needs_Action",
        "Done",
        "Pending_Approval",
        "Accounting",
        "Briefings",
        "Plans",
        "Active_Project",
        "Tasks",
        "Templates",
    ]
    
    required_files = [
        "Dashboard.md",
        "Company_Handbook.md",
        "Business_Goals.md",
    ]
    
    all_passed = True
    
    for dir_name in required_dirs:
        dir_path = vault_path / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"  {dir_name}/ - OK")
        else:
            print(f"  {dir_name}/ - MISSING")
            all_passed = False
    
    for file_name in required_files:
        file_path = vault_path / file_name
        if file_path.exists() and file_path.is_file():
            print(f"  {file_name} - OK")
        else:
            print(f"  {file_name} - MISSING")
            all_passed = False
    
    return all_passed


def test_skills():
    """Verify skills are properly defined."""
    print("\nTesting skills...")
    
    skills_path = Path(__file__).parent.parent / "skills"
    expected_skills = ["vault-processor", "daily-briefing"]
    
    all_passed = True
    for skill in expected_skills:
        skill_path = skills_path / skill / "SKILL.md"
        if skill_path.exists():
            print(f"  {skill}/SKILL.md - OK")
        else:
            print(f"  {skill}/SKILL.md - MISSING")
            all_passed = False
    
    return all_passed


def main():
    """Run the setup and optional validation."""
    parser = len(sys.argv) > 1 and sys.argv[1] == "--test"
    
    print("=" * 50)
    print("AI Employee Watchers - Setup")
    print("=" * 50)
    
    # Always check Python version
    check_python_version()
    
    # Always install dependencies
    install_dependencies()
    
    if parser:
        # Run validation tests
        print("\n" + "=" * 50)
        print("Running Bronze Tier Validation")
        print("=" * 50)
        
        results = {
            "Module Imports": test_imports(),
            "Vault Structure": test_vault_structure(),
            "Skills": test_skills(),
        }
        
        print("\n" + "=" * 50)
        print("Bronze Tier Validation Results")
        print("=" * 50)
        
        all_passed = True
        for test_name, passed in results.items():
            status = "PASS" if passed else "FAIL"
            print(f"  {test_name}: {status}")
            if not passed:
                all_passed = False
        
        print("=" * 50)
        if all_passed:
            print("Bronze Tier: ALL CHECKS PASSED")
        else:
            print("Bronze Tier: SOME CHECKS FAILED")
            print("Review the output above and fix issues.")
        print("=" * 50)
        
        return 0 if all_passed else 1
    else:
        print("\nSetup complete!")
        print("\nNext steps:")
        print("1. Open AI_Employee_Vault in Obsidian")
        print("2. Run: python orchestrator.py ../AI_Employee_Vault")
        print("3. Drop files into AI_Employee_Vault/Inbox/ to test")
        print("\nFor validation, run: python setup.py --test")
        return 0


if __name__ == "__main__":
    sys.exit(main())
