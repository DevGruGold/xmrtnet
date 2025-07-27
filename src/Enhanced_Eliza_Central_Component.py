#!/usr/bin/env python3
"""
🚀 ELIZA LAUNCHER - FIXED DIRECTORY ROUTING
==========================================
Created: 2025-07-27T20:12:35.519963
Purpose: Launch Enhanced_Eliza_Central_Component.py from correct location
"""

import sys
import os
from pathlib import Path

# Add the correct directory to Python path
current_dir = Path(__file__).parent
if current_dir.name == 'src':
    # We're in /src, look for backend/src
    backend_src = current_dir.parent / 'backend' / 'src'
    if backend_src.exists():
        sys.path.insert(0, str(backend_src))
        print(f"🔧 Added {backend_src} to Python path")

# Try to import and run the Enhanced Eliza Central Component
try:
    print("🚀 Starting Enhanced Eliza Central Component...")
    
    # Import the main component
    from Enhanced_Eliza_Central_Component import *
    
    # If there's a main function, run it
    if 'main' in globals():
        main()
    elif '__name__' in globals() and globals()['__name__'] == '__main__':
        # Execute the module's main code
        exec(open('Enhanced_Eliza_Central_Component.py').read())
    else:
        print("✅ Enhanced Eliza Central Component loaded successfully")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("🔍 Searching for Enhanced_Eliza_Central_Component.py...")
    
    # Search for the file
    for root, dirs, files in os.walk('.'):
        if 'Enhanced_Eliza_Central_Component.py' in files:
            file_path = os.path.join(root, 'Enhanced_Eliza_Central_Component.py')
            print(f"📍 Found file at: {file_path}")
            
            # Add directory to path and try again
            sys.path.insert(0, root)
            try:
                exec(open(file_path).read())
                break
            except Exception as exec_error:
                print(f"❌ Execution error: {exec_error}")
                
except Exception as e:
    print(f"❌ Runtime error: {e}")
    print("🔄 Attempting fallback execution...")
    
    # Fallback: find and execute the file directly
    import subprocess
    
    # Search for the actual file
    for root, dirs, files in os.walk('.'):
        if 'Enhanced_Eliza_Central_Component.py' in files:
            file_path = os.path.join(root, 'Enhanced_Eliza_Central_Component.py')
            print(f"🔄 Executing {file_path} directly...")
            
            try:
                result = subprocess.run([sys.executable, file_path], 
                                      capture_output=True, text=True)
                print(result.stdout)
                if result.stderr:
                    print(f"Stderr: {result.stderr}")
                break
            except Exception as subprocess_error:
                print(f"❌ Subprocess error: {subprocess_error}")

if __name__ == "__main__":
    print("🚀 ELIZA LAUNCHER STARTED")
    print("🎯 Mission: Launch Enhanced Eliza Central Component")
