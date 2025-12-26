#!/usr/bin/env python3
"""Verify that the git tag version matches versions in project files.

This script checks that the version from the git tag matches:
- pyproject.toml [project] version
- a2ui_pydantic/__init__.py __version__
- README.md (if version is mentioned)

Usage:
    python scripts/verify_version.py <tag_name>

Example:
    python scripts/verify_version.py v0.1.0
"""

import re
import sys
from pathlib import Path


def extract_version_from_tag(tag: str) -> str:
    """Extract version from git tag (remove 'v' prefix if present)."""
    if tag.startswith("v"):
        return tag[1:]
    return tag


def get_pyproject_version() -> str:
    """Extract version from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print(f"❌ Error: {pyproject_path} not found", file=sys.stderr)
        sys.exit(1)

    content = pyproject_path.read_text(encoding="utf-8")
    # Match version = "x.y.z" or version = 'x.y.z'
    match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        print("❌ Error: Could not find version in pyproject.toml")
        sys.exit(1)

    return match.group(1)


def get_init_version() -> str:
    """Extract version from a2ui_pydantic/__init__.py."""
    init_path = Path("a2ui_pydantic/__init__.py")
    if not init_path.exists():
        print(f"❌ Error: {init_path} not found")
        sys.exit(1)

    content = init_path.read_text(encoding="utf-8")
    # Match __version__ = "x.y.z" or __version__ = 'x.y.z'
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if not match:
        print("❌ Error: Could not find __version__ in a2ui_pydantic/__init__.py")
        sys.exit(1)

    return match.group(1)


def check_readme_version(version: str):
    """Check if version appears in README.md (optional check)."""
    readme_path = Path("README.md")
    if not readme_path.exists():
        return  # README is optional
    content = readme_path.read_text(encoding="utf-8")
    # This is a soft check. We just check for presence of the version string.
    if version in content or f"v{version}" in content:
        print("✅ README.md seems to contain the correct version.")
    else:
        # Warn if it's not present, as it might be an oversight.
        print(
            "⚠️  Warning: Current version not found in README.md. "
            "Please check if it needs to be updated."
        )


def main():
    """Main verification function."""
    if len(sys.argv) != 2:
        print("Usage: python scripts/verify_version.py <tag_name>")
        print("Example: python scripts/verify_version.py v0.1.0")
        sys.exit(1)

    tag_name = sys.argv[1]
    tag_version = extract_version_from_tag(tag_name)

    print(f"🔍 Verifying version consistency for tag: {tag_name}")
    print(f"   Extracted version: {tag_version}\n")

    # Get versions from files
    pyproject_version = get_pyproject_version()
    init_version = get_init_version()

    print(f"📄 pyproject.toml version:        {pyproject_version}")
    print(f"📄 __init__.py __version__:      {init_version}")

    # Check matches
    errors = []
    if tag_version != pyproject_version:
        errors.append(
            f"❌ Tag version ({tag_version}) does not match "
            f"pyproject.toml version ({pyproject_version})"
        )
    else:
        print("✅ Tag version matches pyproject.toml")

    if tag_version != init_version:
        errors.append(
            f"❌ Tag version ({tag_version}) does not match "
            f"__init__.py __version__ ({init_version})"
        )
    else:
        print("✅ Tag version matches __init__.py")

    if pyproject_version != init_version:
        errors.append(
            f"❌ pyproject.toml version ({pyproject_version}) does not match "
            f"__init__.py __version__ ({init_version})"
        )
    else:
        print("✅ pyproject.toml and __init__.py versions match")

    # Check README (soft check)
    check_readme_version(tag_version)

    # Report results
    if errors:
        print("\n❌ Version verification failed:")
        for error in errors:
            print(f"   {error}")
        print("\n💡 Please update the version in:")
        print("   - pyproject.toml")
        print("   - a2ui_pydantic/__init__.py")
        print("   - README.md (if version is mentioned)")
        sys.exit(1)

    print("\n✅ All version checks passed!")
    sys.exit(0)


if __name__ == "__main__":
    main()
