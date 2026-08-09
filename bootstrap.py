import os
import sys

# 1. Force Project Root into Python Path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2. Automatically Create Missing __init__.py Files in All Subdirectories
def ensure_package_structure(root_dir: str):
    targets = ["utils", "industries", "evaluation", "data"]
    for target in targets:
        target_path = os.path.join(root_dir, target)
        if os.path.exists(target_path):
            for current_root, dirs, files in os.walk(target_path):
                # Ignore cache and hidden directories
                if "__pycache__" in current_root or "/." in current_root:
                    continue
                init_file = os.path.join(current_root, "__init__.py")
                if not os.path.exists(init_file):
                    with open(init_file, "w", encoding="utf-8") as f:
                        f.write(f"# Auto-generated package initializer for {os.path.basename(current_root)}\n")
                    print(f"📦 Auto-created package file: {init_file}")

# Run structural check on import
ensure_package_structure(PROJECT_ROOT)
