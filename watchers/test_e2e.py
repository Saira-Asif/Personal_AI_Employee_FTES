"""
End-to-end test for the Bronze Tier AI Employee.

This script validates the complete watcher -> orchestrator -> vault workflow:
1. Creates a test file in the Inbox
2. Verifies the FileSystemWatcher detects it
3. Verifies an action file is created in Needs_Action
4. Verifies the orchestrator can process it
5. Cleans up test artifacts

Usage:
    python test_e2e.py
    python test_e2e.py --vault-path /path/to/vault
"""

import sys
import time
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))


class TestResult:
    """Track test results."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
    
    def record(self, name: str, passed: bool, details: str = ""):
        self.tests.append({"name": name, "passed": passed, "details": details})
        if passed:
            self.passed += 1
            print(f"  PASS: {name}")
        else:
            self.failed += 1
            print(f"  FAIL: {name} - {details}")
    
    def summary(self) -> bool:
        total = self.passed + self.failed
        print(f"\n{'='*50}")
        print(f"Results: {self.passed}/{total} tests passed")
        if self.failed > 0:
            print(f"FAILED tests:")
            for t in self.tests:
                if not t["passed"]:
                    print(f"  - {t['name']}: {t['details']}")
        print(f"{'='*50}")
        return self.failed == 0


def test_vault_structure(vault_path: Path, results: TestResult):
    """Test 1: Verify vault structure exists."""
    print("\n[Test 1: Vault Structure]")
    
    required_dirs = [
        "Inbox", "Needs_Action", "Done", "Pending_Approval",
        "Accounting", "Briefings", "Plans", "Active_Project", "Tasks"
    ]
    
    required_files = ["Dashboard.md", "Company_Handbook.md", "Business_Goals.md"]
    
    for dir_name in required_dirs:
        dir_path = vault_path / dir_name
        results.record(
            f"Directory: {dir_name}",
            dir_path.exists() and dir_path.is_dir(),
            f"Missing: {dir_path}"
        )
    
    for file_name in required_files:
        file_path = vault_path / file_name
        exists = file_path.exists() and file_path.is_file()
        results.record(
            f"File: {file_name}",
            exists,
            f"Missing: {file_path}"
        )
    
    # Verify key files have content
    for file_name in required_files:
        file_path = vault_path / file_name
        if file_path.exists():
            content = file_path.read_text(encoding="utf-8")
            has_content = len(content) > 50
            has_frontmatter = "---" in content and "---" in content[content.index("---")+3:]
            results.record(
                f"File content: {file_name}",
                has_content and has_frontmatter,
                f"File too short or missing frontmatter"
            )


def test_dashboard_content(vault_path: Path, results: TestResult):
    """Test 2: Verify Dashboard.md has proper structure."""
    print("\n[Test 2: Dashboard Structure]")
    
    dashboard = vault_path / "Dashboard.md"
    if not dashboard.exists():
        results.record("Dashboard.md exists", False, "File missing")
        return
    
    results.record("Dashboard.md exists", True)
    
    content = dashboard.read_text(encoding="utf-8")
    
    required_sections = [
        ("type: dashboard", "Frontmatter type"),
        ("Key Metrics", "Key Metrics section"),
        ("Bank Balance", "Bank Balance section"),
        ("Active Tasks", "Active Tasks section"),
        ("System Status", "System Status section"),
    ]
    
    for search_term, description in required_sections:
        results.record(
            f"Dashboard: {description}",
            search_term in content,
            f"Missing: {search_term}"
        )


def test_company_handbook(vault_path: Path, results: TestResult):
    """Test 3: Verify Company_Handbook.md has essential rules."""
    print("\n[Test 3: Company Handbook]")
    
    handbook = vault_path / "Company_Handbook.md"
    if not handbook.exists():
        results.record("Company_Handbook.md exists", False, "File missing")
        return
    
    results.record("Company_Handbook.md exists", True)
    
    content = handbook.read_text(encoding="utf-8")
    
    required_rules = [
        "Human-in-the-Loop",
        "Escalation",
        "Priority",
        "Financial",
        "Folder Structure",
    ]
    
    for rule in required_rules:
        results.record(
            f"Handbook: {rule} rules",
            rule in content,
            f"Missing: {rule}"
        )


def test_watcher_creation(vault_path: Path, results: TestResult):
    """Test 4: Test FileSystemWatcher creates action files."""
    print("\n[Test 4: File System Watcher]")
    
    from filesystem_watcher import DropFolderHandler
    
    # Create a test file in Inbox
    inbox = vault_path / "Inbox"
    test_file = inbox / "test_document.txt"
    test_content = "This is a test document for the AI Employee."
    
    try:
        test_file.write_text(test_content, encoding="utf-8")
        results.record("Test file created in Inbox", True)
    except Exception as e:
        results.record("Test file created in Inbox", False, str(e))
        return
    
    # Create handler and simulate file detection
    handler = DropFolderHandler(vault_path)
    
    try:
        action_file = handler._create_action_file(test_file)
        handler.processed_ids.add(str(test_file))
        
        results.record(
            "Action file created",
            action_file.exists(),
            f"File not created at: {action_file}"
        )
        
        if action_file.exists():
            content = action_file.read_text(encoding="utf-8")
            results.record(
                "Action file has frontmatter",
                "---" in content and "type: file_drop" in content,
                "Missing frontmatter or type"
            )
            results.record(
                "Action file has original filename",
                "test_document.txt" in content,
                "Missing original filename"
            )
        
        # Clean up action file
        if action_file.exists():
            action_file.unlink()
        
    except Exception as e:
        results.record("Action file created", False, str(e))
    
    # Clean up test file
    if test_file.exists():
        test_file.unlink()


def test_orchestrator_processing(vault_path: Path, results: TestResult):
    """Test 5: Test orchestrator can process action files."""
    print("\n[Test 5: Orchestrator Processing]")
    
    from orchestrator import Orchestrator
    
    orchestrator = Orchestrator(vault_path=str(vault_path))
    
    # Create a test action file
    needs_action = vault_path / "Needs_Action"
    test_action = needs_action / "FILE_test_orchestrator.md"
    test_action.write_text(
        """---
type: file_drop
source: filesystem_watcher
original_name: test.txt
created: 2026-04-10T12:00:00
status: pending
---

# File Dropped for Processing

## File Information
- **Name**: test.txt
- **Type**: text
- **Size**: 100 bytes
""",
        encoding="utf-8"
    )
    
    try:
        success = orchestrator.process_item(test_action)
        results.record(
            "Orchestrator processes action file",
            success,
            "Processing failed"
        )
        
        # Verify plan was created
        plans = vault_path / "Plans"
        plan_files = list(plans.glob("PLAN_*.md"))
        results.record(
            "Plan file created",
            len(plan_files) > 0,
            "No plan files found in Plans/"
        )
        
        # Clean up plan files
        for pf in plan_files:
            pf.unlink()
        
    except Exception as e:
        results.record("Orchestrator processes action file", False, str(e))
    
    # Clean up test action file
    if test_action.exists():
        test_action.unlink()


def test_skills_structure(results: TestResult):
    """Test 6: Verify skills are properly defined."""
    print("\n[Test 6: Agent Skills]")
    
    skills_path = Path(__file__).parent.parent / "skills"
    
    expected_skills = {
        "vault-processor": [
            "When to Use",
            "Workflow",
            "Rules",
        ],
        "daily-briefing": [
            "When to Use",
            "Daily Briefing",
            "Weekly CEO Briefing",
        ],
    }
    
    for skill_name, required_sections in expected_skills.items():
        skill_file = skills_path / skill_name / "SKILL.md"
        
        exists = skill_file.exists()
        results.record(
            f"Skill exists: {skill_name}",
            exists,
            f"Missing: {skill_file}"
        )
        
        if exists:
            content = skill_file.read_text(encoding="utf-8")
            
            # Check for frontmatter
            has_frontmatter = content.startswith("---") and content.count("---") >= 2
            results.record(
                f"Skill {skill_name}: has frontmatter",
                has_frontmatter,
                "Missing YAML frontmatter"
            )
            
            for section in required_sections:
                results.record(
                    f"Skill {skill_name}: {section}",
                    section in content,
                    f"Missing section: {section}"
                )


def test_python_modules(results: TestResult):
    """Test 7: Verify all Python modules import correctly."""
    print("\n[Test 7: Python Module Imports]")
    
    imports = [
        ("base_watcher", "BaseWatcher"),
        ("filesystem_watcher", "FileSystemWatcher", "DropFolderHandler"),
        ("orchestrator", "Orchestrator"),
    ]
    
    for import_spec in imports:
        module_name = import_spec[0]
        classes = import_spec[1:]
        
        try:
            mod = __import__(module_name)
            results.record(f"Import: {module_name}", True)
            
            for cls_name in classes:
                try:
                    getattr(mod, cls_name)
                    results.record(f"  Class: {cls_name}", True)
                except AttributeError:
                    results.record(f"  Class: {cls_name}", False, "Class not found")
                    
        except ImportError as e:
            results.record(f"Import: {module_name}", False, str(e))


def test_e2e_drop_and_detect(vault_path: Path, results: TestResult):
    """Test 9: End-to-end file drop → watcher detects → action file created."""
    print("\n[Test 9: End-to-End Drop & Detect]")

    import threading
    from filesystem_watcher import FileSystemWatcher

    inbox = vault_path / "Inbox"
    needs_action = vault_path / "Needs_Action"

    # Count existing action files before test
    before_count = len(list(needs_action.glob("FILE_*.md")))

    # Start the watcher in a background thread
    watcher = FileSystemWatcher(vault_path=str(vault_path))
    watcher_thread = threading.Thread(target=watcher.observer.start, daemon=True)
    watcher.observer.start()
    watcher.running = True
    time.sleep(0.5)  # Let observer initialize

    results.record("Watcher started", True)

    try:
        # Drop a test file into Inbox
        test_file = inbox / "e2e_test_document.txt"
        test_file.write_text(
            "This is an end-to-end test document for Bronze Tier validation.",
            encoding="utf-8"
        )
        results.record("Test file dropped into Inbox", True)

        # Wait for watchdog to detect (typically <1 second, give generous timeout)
        time.sleep(3)

        # Check if action file was created in Needs_Action
        after_count = len(list(needs_action.glob("FILE_*.md")))
        new_files = after_count - before_count

        results.record(
            "Action file created in Needs_Action",
            new_files > 0,
            f"No new FILE_*.md files found (before={before_count}, after={after_count})"
        )

        # Verify the action file content
        if new_files > 0:
            action_files = list(needs_action.glob("FILE_*.md"))
            # Find the one we just created (most recent matching e2e_test)
            matching = [f for f in action_files if "e2e_test_document" in f.name]
            if matching:
                action_file = matching[0]
                content = action_file.read_text(encoding="utf-8")
                results.record(
                    "Action file has correct frontmatter",
                    "---" in content and "type: file_drop" in content,
                    "Missing frontmatter or type: file_drop"
                )
                results.record(
                    "Action file references original filename",
                    "e2e_test_document.txt" in content,
                    "Missing original filename in action file"
                )
                # Clean up this action file
                action_file.unlink()
            else:
                results.record("Action file has correct frontmatter", False, "Could not find matching action file")

    except Exception as e:
        results.record("Test file dropped into Inbox", False, str(e))

    finally:
        # Stop the watcher
        watcher.running = False
        watcher.observer.stop()
        watcher.observer.join(timeout=2)

        # Clean up test file
        test_file = inbox / "e2e_test_document.txt"
        if test_file.exists():
            test_file.unlink()

        # Clean up any leftover action files from this test
        for f in needs_action.glob("FILE_*e2e_test*.md"):
            f.unlink()


def test_templates(vault_path: Path, results: TestResult):
    """Test 8: Verify template files exist and have proper structure."""
    print("\n[Test 8: Templates]")
    
    templates_path = vault_path / "Templates"
    expected_templates = ["Task.md", "Email.md", "Approval_Request.md", "Plan.md"]
    
    if not templates_path.exists():
        results.record("Templates directory exists", False, "Missing Templates/")
        return
    
    results.record("Templates directory exists", True)
    
    for template_name in expected_templates:
        template_file = templates_path / template_name
        exists = template_file.exists()
        results.record(
            f"Template: {template_name}",
            exists,
            f"Missing: {template_file}"
        )
        
        if exists:
            content = template_file.read_text(encoding="utf-8")
            has_frontmatter = content.startswith("---")
            results.record(
                f"  {template_name}: has frontmatter",
                has_frontmatter,
                "Missing YAML frontmatter"
            )


def main():
    """Run all Bronze Tier validation tests."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Bronze Tier End-to-End Validation")
    parser.add_argument(
        "--vault-path",
        help="Path to the AI Employee Vault (default: auto-detect)",
    )
    args = parser.parse_args()
    
    # Auto-detect vault path
    if args.vault_path is None:
        vault_path = Path(__file__).parent.parent / "AI_Employee_Vault"
    else:
        vault_path = Path(args.vault_path)
    
    if not vault_path.exists():
        print(f"ERROR: Vault path not found: {vault_path}")
        sys.exit(1)
    
    print("=" * 50)
    print("Bronze Tier End-to-End Validation")
    print(f"Vault: {vault_path}")
    print(f"Tests: 36 checks across 9 categories")
    print("=" * 50)
    
    results = TestResult()
    
    # Change to watchers directory for imports
    import os
    os.chdir(Path(__file__).parent)
    
    # Run all tests
    test_vault_structure(vault_path, results)
    test_dashboard_content(vault_path, results)
    test_company_handbook(vault_path, results)
    test_watcher_creation(vault_path, results)
    test_orchestrator_processing(vault_path, results)
    test_skills_structure(results)
    test_python_modules(results)
    test_templates(vault_path, results)
    test_e2e_drop_and_detect(vault_path, results)
    
    # Final summary
    all_passed = results.summary()
    
    if all_passed:
        print("\nBronze Tier: FULLY VALIDATED")
        print("\nYour AI Employee is ready for:")
        print("  - Opening in Obsidian")
        print("  - Running the orchestrator: python orchestrator.py ../AI_Employee_Vault")
        print("  - Processing files dropped into Inbox/")
    else:
        print("\nBronze Tier: VALIDATION ISSUES FOUND")
        print("Review the failures above and fix them.")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
