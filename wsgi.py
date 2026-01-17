"""
WSGI configuration for PythonAnywhere
GestorEventos v2.0
"""

import sys
import os

# Add your project directory to the sys.path
project_home = '/home/YOUR_USERNAME/GestorEventos'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set environment variables
os.environ['FLASK_ENV'] = 'production'
os.environ['DEBUG'] = 'False'

# Import the Flask app
from run import app as application
