import subprocess
import sys
import os

def install():
    print(f"Using executable: {sys.executable}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pymysql"])
        print("Installation successful")
    except Exception as e:
        print(f"Installation failed: {e}")

if __name__ == "__main__":
    install()
