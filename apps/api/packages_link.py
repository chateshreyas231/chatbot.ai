"""Create symlink to packages for easier imports."""
import sys
from pathlib import Path

# Add packages to Python path
packages_path = Path(__file__).parent.parent.parent / "packages"
if str(packages_path) not in sys.path:
    sys.path.insert(0, str(packages_path))

