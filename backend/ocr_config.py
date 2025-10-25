"""
OCR Configuration for Tesseract
"""

import os
import pytesseract

# Configure Tesseract path for Windows
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def configure_tesseract():
    """Configure pytesseract with correct path"""
    if os.path.exists(TESSERACT_PATH):
        pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
        return True
    else:
        # Try to find tesseract in PATH
        try:
            import subprocess
            result = subprocess.run(['tesseract', '--version'],
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return True
        except:
            pass
        return False

def get_tesseract_version():
    """Get Tesseract version info"""
    try:
        version = pytesseract.get_tesseract_version()
        return str(version)
    except Exception as e:
        return f"Error: {e}"

# Auto-configure on import
if not configure_tesseract():
    print("⚠️ Warning: Tesseract not found. OCR features may not work properly.")
    print("Please install Tesseract from: https://github.com/tesseract-ocr/tesseract")
    print("Or ensure it's in your PATH environment variable.")