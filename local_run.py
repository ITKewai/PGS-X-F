import os
import subprocess
import sys


def run(cmd):
    print(f"\n[*] {cmd}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        sys.exit(result.returncode)


# 1. Set UTF-8 (facoltativo su Python)
os.system('chcp 65001 >nul')

# 2. Install dependencies
# run("pip install --upgrade pip")
if os.path.exists("requirements.txt"):
    run("pip install -r requirements.txt")
run("pip install pyinstaller")

# 3. Generate version file if exists
if os.path.exists("make_version_file.py"):
    run("python make_version_file.py")

# 4. Build with PyInstaller
run("pyinstaller main.spec")
run(" del .\\version_info.txt")
run(" del build")
print("\n✅ Build completata! Controlla la cartella dist/")
