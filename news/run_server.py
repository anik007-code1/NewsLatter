#!/usr/bin/env python
"""
Convenience script to run the Django development server
"""
import os
import sys
import subprocess

def main():
    """Run the Django development server"""
    # Change to the project directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Activate virtual environment and run server
    if os.name == 'nt':  # Windows
        activate_script = 'venv\\Scripts\\activate.bat'
        command = f'{activate_script} && python manage.py runserver'
        subprocess.run(command, shell=True)
    else:  # Unix/Linux/macOS
        activate_script = 'source venv/bin/activate'
        command = f'{activate_script} && python manage.py runserver'
        subprocess.run(command, shell=True, executable='/bin/bash')

if __name__ == '__main__':
    main()
