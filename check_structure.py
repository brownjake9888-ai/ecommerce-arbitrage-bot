"""Verify project structure and functionality."""
import os
import sys

def check_files():
    """Check if all required files exist."""
    required_files = [
        'bot.py',
        'config.py',
        'database.py',
        'scraper.py',
        'stealth.py',
        'filter.py',
        'profit_calculator.py',
        'ebay_lister.py',
        'telegram_notifier.py',
        'requirements.txt',
        '.env.example',
        '.gitignore',
        'README.md',
        'QUICKSTART.md',
        'demo.py',
    ]
    
    print("Checking project structure...")
    print("=" * 60)
    
    all_exist = True
    for file in required_files:
        exists = os.path.exists(file)
        status = "✓" if exists else "✗"
        print(f"{status} {file}")
        if not exists:
            all_exist = False
    
    return all_exist

def check_imports():
    """Check if core modules can be imported."""
    print("\n" + "=" * 60)
    print("Checking core module imports...")
    print("=" * 60)
    
    core_modules = [
        'config',
        'database',
        'stealth',
        'profit_calculator',
        'filter',
    ]
    
    all_imported = True
    for module in core_modules:
        try:
            __import__(module)
            print(f"✓ {module}")
        except Exception as e:
            print(f"✗ {module}: {e}")
            all_imported = False
    
    return all_imported

def count_lines():
    """Count total lines of code."""
    print("\n" + "=" * 60)
    print("Code statistics...")
    print("=" * 60)
    
    python_files = [
        'bot.py',
        'config.py',
        'database.py',
        'scraper.py',
        'stealth.py',
        'filter.py',
        'profit_calculator.py',
        'ebay_lister.py',
        'telegram_notifier.py',
        'demo.py',
    ]
    
    total_lines = 0
    for file in python_files:
        if os.path.exists(file):
            with open(file, 'r') as f:
                lines = len(f.readlines())
                total_lines += lines
                print(f"  {file}: {lines} lines")
    
    print(f"\nTotal: {total_lines} lines of Python code")

def main():
    """Run all checks."""
    print("\n" + "=" * 70)
    print(" " * 15 + "PROJECT STRUCTURE VERIFICATION")
    print("=" * 70 + "\n")
    
    files_ok = check_files()
    imports_ok = check_imports()
    count_lines()
    
    print("\n" + "=" * 70)
    if files_ok and imports_ok:
        print("✅ All checks passed! Project is ready to use.")
        print("\nNext steps:")
        print("  1. Install all dependencies: pip install -r requirements.txt")
        print("  2. Configure .env with your API keys")
        print("  3. Run demo: python demo.py")
        print("  4. Run bot: python bot.py")
    else:
        print("⚠️  Some checks failed. Review errors above.")
        sys.exit(1)
    print("=" * 70 + "\n")

if __name__ == '__main__':
    main()
