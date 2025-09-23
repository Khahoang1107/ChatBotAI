"""
Development setup script for the Invoice Management Backend API
Run this script to set up the development environment
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True


def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    try:
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        return False


def install_dependencies():
    """Install Python dependencies"""
    try:
        print("📦 Installing dependencies...")
        
        # Determine the correct pip path
        if os.name == 'nt':  # Windows
            pip_path = Path("venv/Scripts/pip")
        else:  # Unix/Linux/macOS
            pip_path = Path("venv/bin/pip")
        
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    env_path = Path(".env")
    env_example_path = Path(".env.example")
    
    if env_path.exists():
        print("✅ .env file already exists")
        return True
    
    if not env_example_path.exists():
        print("❌ .env.example file not found")
        return False
    
    try:
        # Copy .env.example to .env
        with open(env_example_path, 'r') as src:
            content = src.read()
        
        with open(env_path, 'w') as dst:
            dst.write(content)
        
        print("✅ .env file created from .env.example")
        print("⚠️  Please update .env with your actual configuration values")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False


def create_directories():
    """Create necessary directories"""
    directories = ["uploads", "logs", "backups"]
    
    for directory in directories:
        dir_path = Path(directory)
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory already exists: {directory}")


def initialize_database():
    """Initialize the database"""
    try:
        print("🗄️  Initializing database...")
        
        # Import and initialize
        from app import create_app
        from utils.database import init_database
        
        app = create_app()
        with app.app_context():
            success = init_database()
            if success:
                print("✅ Database initialized successfully")
                return True
            else:
                print("❌ Database initialization failed")
                return False
                
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False


def check_dependencies():
    """Check if required system dependencies are installed"""
    dependencies = {
        'tesseract': 'Tesseract OCR engine',
        'poppler': 'Poppler PDF utilities (for pdf2image)'
    }
    
    print("🔍 Checking system dependencies...")
    
    # Check Tesseract
    try:
        subprocess.run(['tesseract', '--version'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
        print("✅ Tesseract OCR is installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Tesseract OCR not found. Please install:")
        print("   Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
        print("   macOS: brew install tesseract")
        print("   Ubuntu: sudo apt-get install tesseract-ocr")
    
    # Check Poppler (for PDF processing)
    try:
        subprocess.run(['pdftoppm', '-h'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL, 
                      check=True)
        print("✅ Poppler PDF utilities are installed")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Poppler not found. Please install:")
        print("   Windows: Download from http://blog.alivate.com.au/poppler-windows/")
        print("   macOS: brew install poppler")
        print("   Ubuntu: sudo apt-get install poppler-utils")


def display_next_steps():
    """Display next steps for the user"""
    print("\n" + "="*50)
    print("🎉 Setup completed successfully!")
    print("="*50)
    print("\n📋 Next steps:")
    print("1. Activate the virtual environment:")
    
    if os.name == 'nt':  # Windows
        print("   venv\\Scripts\\activate")
    else:  # Unix/Linux/macOS
        print("   source venv/bin/activate")
    
    print("\n2. Update .env file with your configuration:")
    print("   - Set OPENAI_API_KEY for AI-powered OCR")
    print("   - Configure database settings if needed")
    print("   - Set email settings for notifications")
    
    print("\n3. Run the development server:")
    print("   python app.py")
    
    print("\n4. Test the API:")
    print("   curl http://localhost:5000/health")
    
    print("\n📚 API Documentation:")
    print("   Check README.md for detailed API documentation")
    print("   Default admin credentials: admin / admin123")
    
    print("\n🔧 Development tools:")
    print("   - Run tests: pytest")
    print("   - Format code: black .")
    print("   - Lint code: flake8")


def main():
    """Main setup function"""
    print("🚀 Setting up Invoice Management Backend API")
    print("=" * 50)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Creating .env file", create_env_file),
        ("Creating directories", create_directories),
        ("Checking system dependencies", check_dependencies),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    # Initialize database (optional, may fail if dependencies not installed)
    print(f"\n📋 Initializing database...")
    try:
        if not initialize_database():
            print("⚠️  Database initialization failed - you can run this later")
    except Exception as e:
        print(f"⚠️  Database initialization skipped: {e}")
        print("   You can initialize it later by running:")
        print("   python -c \"from app import create_app; from utils.database import init_database; app = create_app(); app.app_context().push(); init_database()\"")
    
    display_next_steps()


if __name__ == "__main__":
    main()