# Add parent directory to Python path for imports
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))