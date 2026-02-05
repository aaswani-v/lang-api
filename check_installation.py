#!/usr/bin/env python
"""
Quick installation verification script
Tests if all core dependencies are installed
"""

print("=" * 60)
print("वाणीCheck - Installation Verification")
print("=" * 60)
print()

modules_to_check = [
    ("fastapi", "FastAPI"),
    ("uvicorn", "Uvicorn"),
    ("pydantic", "Pydantic"),
    ("torch", "PyTorch"),
    ("torchaudio", "TorchAudio"),
    ("transformers", "Transformers"),
    ("librosa", "Librosa"),
    ("scipy", "SciPy"),
    ("soundfile", "SoundFile"),
    ("pytest", "PyTest"),
    ("httpx", "HTTPX"),
]

all_good = True
print("Checking installed packages:\n")

for module_name, display_name in modules_to_check:
    try:
        mod = __import__(module_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"✓ {display_name:20} {version}")
    except ImportError:
        print(f"✗ {display_name:20} NOT INSTALLED")
        all_good = False

print()
print("=" * 60)

if all_good:
    print("✓ ALL DEPENDENCIES INSTALLED SUCCESSFULLY!")
    print()
    print("Next steps:")
    print("1. Start the API: python main.py")
    print("   Or: start_api.bat (Windows)")
    print()
    print("2. Access API docs: http://localhost:8000/docs")
    print()
    print("3. Run verification: python verify_api.py")
    print()
    print("4. Run tests: pytest tests/test_main.py -v")
else:
    print("✗ SOME PACKAGES MISSING")
    print("Run: pip install -r requirements.txt")

print("=" * 60)
