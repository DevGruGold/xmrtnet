"""
CRITICAL STOP MODULE - Prevents fake task execution
This module terminates any script that tries to run fake cycles
"""

import sys
import os

def enforce_no_fake_tasks():
    """Enforce the no fake tasks policy"""
    
    # Check for stop flag
    if os.path.exists('STOP_FAKE_TASKS.flag'):
        try:
            with open('STOP_FAKE_TASKS.flag', 'r') as f:
                if 'STOP_FAKE_TASKS=true' in f.read():
                    print("🛑 FAKE TASK EXECUTION TERMINATED")
                    print("📋 Task verification system must be implemented")
                    print("❌ Cycle-based fake tasks are prohibited")
                    sys.exit(0)
        except:
            pass
    
    # Check environment variable
    if os.getenv('STOP_FAKE_TASKS') == 'true':
        print("🛑 FAKE TASK EXECUTION TERMINATED (ENV VAR)")
        sys.exit(0)

# Auto-execute when module is imported
enforce_no_fake_tasks()
