#!/usr/bin/env python3
# setup_assistant.py - Interactive setup assistant for Mudhumeni AI on macOS

import subprocess
import os
import platform
import sys
import shutil
from pathlib import Path

def print_color(text, color="green"):
    """Print colored text to terminal"""
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "end": "\033[0m"
    }
    print(f"{colors.get(color, colors['green'])}{text}{colors['end']}")

def check_system():
    """Check if running on macOS"""
    if platform.system() != "Darwin":
        print_color("This script is intended for macOS only!", "red")
        sys.exit(1)
    print_color(f"Detected macOS {platform.mac_ver()[0]}", "green")

def check_python():
    """Check Python version"""
    version = platform.python_version()
    print_color(f"Python version: {version}", "blue")
    if version < "3.9":
        print_color("Warning: This project was developed with Python 3.9+. You may encounter issues.", "yellow")
    return version

def check_homebrew():
    """Check if Homebrew is installed"""
    try:
        result = subprocess.run(['brew', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print_color(f"Homebrew is installed: {result.stdout.split()[0]} {result.stdout.split()[1]}", "green")
            return True
    except FileNotFoundError:
        print_color("Homebrew is not installed. It's recommended for installing dependencies.", "yellow")
        print("Install Homebrew? (y/n)")
        if input().lower() == 'y':
            print_color("Installing Homebrew...", "blue")
            subprocess.run(['/bin/bash', '-c', '$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)'])
            return True
    return False

def setup_project_directory():
    """Set up project directory"""
    home = Path.home()
    project_dir = home / "Projects" / "Mudhumeni_AI"
    
    if project_dir.exists():
        print_color(f"Project directory already exists at {project_dir}", "green")
    else:
        project_dir.mkdir(parents=True, exist_ok=True)
        print_color(f"Created project directory at {project_dir}", "green")
    
    return project_dir

def create_virtual_env(project_dir):
    """Create and activate virtual environment"""
    venv_dir = project_dir / "venv"
    
    if venv_dir.exists():
        print_color("Virtual environment already exists", "green")
    else:
        print_color("Creating virtual environment...", "blue")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)])
        print_color("Virtual environment created", "green")
    
    # Return activation command (we can't actually activate from within Python)
    if platform.system() == "Darwin":  # macOS
        return f"source {venv_dir}/bin/activate"
    else:
        return f"{venv_dir}\\Scripts\\activate"

def create_requirements_file(project_dir):
    """Create requirements.txt file"""
    req_file = project_dir / "requirements.txt"
    
    if req_file.exists():
        print_color("requirements.txt already exists", "green")
    else:
        print_color("Creating requirements.txt...", "blue")
        with open(req_file, 'w') as f:
            f.write("""flask==2.0.1
langchain-groq==0.0.6
numpy==1.22.3
pandas==1.4.2
scikit-learn==1.0.2
requests==2.27.1
gunicorn==20.1.0
Werkzeug==2.3.7
python-dotenv==0.20.0
pymongo==4.1.1
""")
        print_color("requirements.txt created", "green")
    
    return req_file

def create_env_file(project_dir):
    """Create .env file"""
    env_file = project_dir / ".env"
    
    if env_file.exists():
        print_color(".env file already exists", "green")
    else:
        print_color("Creating .env file...", "blue")
        with open(env_file, 'w') as f:
            f.write("""# Mudhumeni AI Environment Variables
FLASK_SECRET_KEY=replace_with_your_secret_key
GROQ_API_KEY=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
# MongoDB Connection (if needed)
MONGODB_URI=mongodb://localhost:27017/
""")
        print_color(".env file created", "green")
    
    return env_file

def check_mongodb():
    """Check if MongoDB is installed via Homebrew"""
    try:
        result = subprocess.run(['brew', 'list', 'mongodb-community'], capture_output=True, text=True)
        if result.returncode == 0:
            print_color("MongoDB is installed via Homebrew", "green")
            
            # Check if MongoDB is running
            service_result = subprocess.run(['brew', 'services', 'list'], capture_output=True, text=True)
            if "mongodb-community started" in service_result.stdout:
                print_color("MongoDB is running", "green")
            else:
                print_color("MongoDB is installed but not running", "yellow")
                print("Start MongoDB? (y/n)")
                if input().lower() == 'y':
                    subprocess.run(['brew', 'services', 'start', 'mongodb-community'])
            return True
    except (FileNotFoundError, subprocess.CalledProcessError):
        print_color("MongoDB is not installed via Homebrew", "yellow")
        if shutil.which('mongod'):
            print_color("MongoDB is installed but not via Homebrew", "yellow")
            return True
        else:
            print("Install MongoDB? (y/n)")
            if input().lower() == 'y':
                print_color("Installing MongoDB...", "blue")
                subprocess.run(['brew', 'tap', 'mongodb/brew'])
                subprocess.run(['brew', 'install', 'mongodb-community'])
                subprocess.run(['brew', 'services', 'start', 'mongodb-community'])
                return True
    return False

def main():
    print_color("=" * 40, "cyan")
    print_color("Mudhumeni AI macOS Setup Assistant", "cyan")
    print_color("=" * 40, "cyan")
    
    check_system()
    check_python()
    has_homebrew = check_homebrew()
    
    project_dir = setup_project_directory()
    venv_activate_cmd = create_virtual_env(project_dir)
    req_file = create_requirements_file(project_dir)
    env_file = create_env_file(project_dir)
    
    if has_homebrew:
        check_mongodb()
    
    print_color("\nSetup completed successfully!", "green")
    print_color("\nNext steps:", "yellow")
    print_color(f"1. Navigate to project directory: cd {project_dir}", "blue")
    print_color(f"2. Activate virtual environment: {venv_activate_cmd}", "blue")
    print_color(f"3. Install dependencies: pip install -r {req_file.name}", "blue")
    print_color(f"4. Edit .env file with your actual API keys: nano {env_file}", "blue")
    print_color("5. Transfer your project files from Windows to the project directory", "blue")
    print_color("6. Run the application: python app.py", "blue")
    
    print_color("\nHappy farming with Mudhumeni AI!", "magenta")

if __name__ == "__main__":
    main()