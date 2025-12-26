#!/usr/bin/env python3
"""
Setup script for Threat-Aware Training Recommender
Automates the initial setup and configuration process
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def run_command(command, check=True, capture_output=False):
    """Run a shell command with error handling."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            check=check, 
            capture_output=capture_output,
            text=True
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        return None


def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def check_ollama():
    """Check if Ollama is installed and running."""
    print("\n📦 Checking Ollama installation...")
    
    # Check if ollama command exists
    result = run_command("ollama --version", check=False, capture_output=True)
    if result is None or result.returncode != 0:
        print("❌ Ollama is not installed")
        print("Please install Ollama from https://ollama.com")
        return False
    
    print("✅ Ollama is installed")
    
    # Check if ollama is running
    result = run_command("ollama list", check=False, capture_output=True)
    if result is None or result.returncode != 0:
        print("⚠️  Ollama server is not running")
        print("Please start Ollama with: ollama serve")
        return False
    
    print("✅ Ollama server is running")
    
    # Check if phi4 model is available
    if "phi4" not in result.stdout:
        print("📥 Pulling phi4 model...")
        pull_result = run_command("ollama pull phi4", check=False)
        if pull_result is None or pull_result.returncode != 0:
            print("❌ Failed to pull phi4 model")
            return False
        print("✅ phi4 model is ready")
    else:
        print("✅ phi4 model is available")
    
    return True


def create_virtual_environment():
    """Create Python virtual environment."""
    print("\n🐍 Setting up Python virtual environment...")
    
    if os.path.exists("venv"):
        print("✅ Virtual environment already exists")
        return True
    
    result = run_command(f"{sys.executable} -m venv venv")
    if result is None:
        print("❌ Failed to create virtual environment")
        return False
    
    print("✅ Virtual environment created")
    return True


def install_dependencies():
    """Install Python dependencies."""
    print("\n📚 Installing Python dependencies...")
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip")
    else:  # Unix/Linux/Mac
        pip_path = os.path.join("venv", "bin", "pip")
    
    # Upgrade pip first
    result = run_command(f"{pip_path} install --upgrade pip")
    if result is None:
        print("⚠️  Failed to upgrade pip")
    
    # Install requirements
    result = run_command(f"{pip_path} install -r requirements.txt")
    if result is None:
        print("❌ Failed to install dependencies")
        return False
    
    print("✅ Dependencies installed successfully")
    return True


def setup_environment():
    """Set up environment configuration."""
    print("\n⚙️  Setting up environment configuration...")
    
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return True
    
    try:
        shutil.copy(".env.example", ".env")
        print("✅ Created .env file from template")
        print("📝 Please edit .env file with your specific settings")
        return True
    except FileNotFoundError:
        print("❌ .env.example file not found")
        return False
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_directories():
    """Create necessary directories."""
    print("\n📁 Creating required directories...")
    
    directories = ["uploads", "model_cache", "logs"]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created {directory}/ directory")
    
    return True


def test_installation():
    """Test the installation by running basic imports."""
    print("\n🧪 Testing installation...")
    
    # Determine the correct python path
    if os.name == 'nt':  # Windows
        python_path = os.path.join("venv", "Scripts", "python")
    else:  # Unix/Linux/Mac
        python_path = os.path.join("venv", "bin", "python")
    
    test_script = '''
import sys
try:
    import flask
    import pandas
    import sentence_transformers
    import ollama
    import requests
    import bs4
    print("✅ All critical dependencies imported successfully")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
'''
    
    result = run_command(f'{python_path} -c "{test_script}"', check=False)
    if result is None or result.returncode != 0:
        print("❌ Installation test failed")
        return False
    
    return True


def main():
    """Main setup function."""
    print("🚀 Threat-Aware Training Recommender Setup")
    print("=" * 50)
    
    # Check prerequisites
    if not check_python_version():
        sys.exit(1)
    
    if not check_ollama():
        print("\n⚠️  Please install and configure Ollama before continuing")
        sys.exit(1)
    
    # Setup steps
    steps = [
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Setting up environment", setup_environment),
        ("Creating directories", create_directories),
        ("Testing installation", test_installation),
    ]
    
    for step_name, step_function in steps:
        if not step_function():
            print(f"\n❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your specific settings")
    print("2. Activate virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Start the application:")
    print("   python app.py")
    print("4. Open http://localhost:5000 in your browser")
    
    print("\n📖 For more information, see README.md")


if __name__ == "__main__":
    main()