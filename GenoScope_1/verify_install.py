#!/usr/bin/env python3
"""
Verify GenoScope dependencies are installed correctly
Run: python verify_install.py
"""

import sys

def check_package(name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = name
    
    try:
        __import__(import_name)
        print(f"✅ {name:20} - Installed")
        return True
    except ImportError:
        print(f"❌ {name:20} - NOT FOUND")
        return False

def main():
    print("=" * 60)
    print("  🧬 GenoScope Dependency Check")
    print("=" * 60)
    print()
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"Python Version: {python_version}")
    
    if sys.version_info < (3, 8):
        print("⚠️  Warning: Python 3.8+ recommended")
    else:
        print("✅ Python version is good")
    
    print("\nChecking GenoScope dependencies:")
    print("-" * 60)
    
    # Check core packages needed for GenoScope
    required_packages = [
        ("aiohttp", "aiohttp"),
        ("pandas", "pandas"),
        ("numpy", "numpy"),
        ("biopython", "Bio"),
        ("streamlit", "streamlit"),
        ("fastapi", "fastapi"),
        ("pydantic", "pydantic"),
        ("uvicorn", "uvicorn"),
        ("python-dotenv", "dotenv"),
    ]
    
    all_installed = True
    for package_name, import_name in required_packages:
        if not check_package(package_name, import_name):
            all_installed = False
    
    print()
    print("=" * 60)
    
    if all_installed:
        print("✅ All GenoScope dependencies are installed!")
        print()
        print("Next steps:")
        print("1. Get your NCBI API key:")
        print("   https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/")
        print()
        print("2. Set your API key:")
        print("   set NCBI_API_KEY=your_key_here")
        print()
        print("3. Start building! Copy the MCP server and agent code")
        print("   to your src/ folder and try running examples.")
    else:
        print("❌ Some packages are missing")
        print()
        print("Run: python -m pip install -r requirements.txt")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
