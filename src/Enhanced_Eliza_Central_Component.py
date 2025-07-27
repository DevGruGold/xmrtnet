#!/usr/bin/env python3
"""
🚀 ELIZA SINGLETON MANAGER - PREVENTS MULTIPLE INSTANCES
======================================================
Created: 2025-07-27T20:24:41.205171
Purpose: Ensure only ONE Enhanced Eliza Central Component runs at a time
Author: DevGruGold (joeyleepcs@gmail.com)

This script:
- Checks for existing Eliza processes
- Kills duplicate instances
- Starts a single, clean Eliza instance
- Maintains a PID lock file
- Monitors and prevents resource conflicts
"""

import os
import sys
import time
import signal
import psutil
import threading
import logging
from pathlib import Path
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s 🚀 [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('eliza_singleton.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger('ELIZA_SINGLETON')

class ElizaSingletonManager:
    """Manages single instance of Enhanced Eliza Central Component"""
    
    def __init__(self):
        self.pid_file = "eliza_instance.pid"
        self.lock_file = "eliza_instance.lock"
        self.component_name = "Enhanced_Eliza_Central_Component"
        self.is_running = False
        
    def check_existing_instances(self):
        """Check for existing Eliza processes"""
        logger.info("🔍 Checking for existing Eliza instances...")
        
        existing_processes = []
        
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if self.component_name in cmdline or 'Enhanced_Eliza' in cmdline:
                        existing_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmdline': cmdline
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                    
        except Exception as e:
            logger.warning(f"Error checking processes: {e}")
            
        logger.info(f"📊 Found {len(existing_processes)} existing Eliza processes")
        return existing_processes
        
    def kill_existing_instances(self):
        """Kill all existing Eliza instances"""
        logger.info("🔪 Terminating existing Eliza instances...")
        
        existing = self.check_existing_instances()
        killed_count = 0
        
        for proc_info in existing:
            try:
                pid = proc_info['pid']
                if pid != os.getpid():  # Don't kill ourselves!
                    logger.info(f"🔪 Terminating PID {pid}: {proc_info['cmdline'][:100]}")
                    
                    try:
                        # Try graceful termination first
                        os.kill(pid, signal.SIGTERM)
                        time.sleep(2)
                        
                        # Check if still running
                        if psutil.pid_exists(pid):
                            logger.warning(f"⚡ Force killing PID {pid}")
                            os.kill(pid, signal.SIGKILL)
                            
                        killed_count += 1
                        
                    except ProcessLookupError:
                        logger.info(f"✅ PID {pid} already terminated")
                    except PermissionError:
                        logger.warning(f"❌ No permission to kill PID {pid}")
                        
            except Exception as e:
                logger.error(f"Error killing process: {e}")
                
        logger.info(f"✅ Terminated {killed_count} existing instances")
        return killed_count
        
    def create_pid_lock(self):
        """Create PID lock file"""
        try:
            pid_info = {
                'pid': os.getpid(),
                'start_time': datetime.now().isoformat(),
                'component': self.component_name,
                'status': 'running'
            }
            
            with open(self.pid_file, 'w') as f:
                json.dump(pid_info, f, indent=2)
                
            # Also create simple lock file
            with open(self.lock_file, 'w') as f:
                f.write(str(os.getpid()))
                
            logger.info(f"🔒 Created PID lock: {os.getpid()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create PID lock: {e}")
            return False
            
    def remove_pid_lock(self):
        """Remove PID lock files"""
        try:
            for lock_file in [self.pid_file, self.lock_file]:
                if os.path.exists(lock_file):
                    os.remove(lock_file)
                    logger.info(f"🗑️ Removed lock file: {lock_file}")
        except Exception as e:
            logger.warning(f"Error removing lock files: {e}")
            
    def check_lock_validity(self):
        """Check if existing lock is valid"""
        try:
            if not os.path.exists(self.pid_file):
                return False
                
            with open(self.pid_file, 'r') as f:
                pid_info = json.load(f)
                
            locked_pid = pid_info.get('pid')
            
            # Check if PID still exists
            if locked_pid and psutil.pid_exists(locked_pid):
                logger.warning(f"⚠️ Valid lock exists for PID {locked_pid}")
                return True
            else:
                logger.info("🗑️ Stale lock found - removing")
                self.remove_pid_lock()
                return False
                
        except Exception as e:
            logger.warning(f"Error checking lock validity: {e}")
            return False
            
    def find_eliza_component(self):
        """Find the actual Enhanced Eliza Central Component file"""
        possible_locations = [
            "Enhanced_Eliza_Central_Component.py",
            "src/Enhanced_Eliza_Central_Component.py", 
            "backend/src/Enhanced_Eliza_Central_Component.py",
            "../Enhanced_Eliza_Central_Component.py",
            "../src/Enhanced_Eliza_Central_Component.py",
            "../backend/src/Enhanced_Eliza_Central_Component.py"
        ]
        
        for location in possible_locations:
            if os.path.exists(location):
                logger.info(f"📍 Found Eliza component at: {location}")
                return location
                
        # Search recursively
        logger.info("🔍 Searching recursively for Eliza component...")
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file == 'Enhanced_Eliza_Central_Component.py':
                    full_path = os.path.join(root, file)
                    logger.info(f"📍 Found Eliza component at: {full_path}")
                    return full_path
                    
        logger.error("❌ Could not find Enhanced_Eliza_Central_Component.py")
        return None
        
    def start_single_eliza_instance(self):
        """Start a single, clean Eliza instance"""
        logger.info("🚀 Starting single Eliza instance...")
        
        # Find the component file
        component_path = self.find_eliza_component()
        if not component_path:
            logger.error("❌ Cannot start - component file not found")
            return False
            
        try:
            # Set environment variables for singleton mode
            os.environ['ELIZA_SINGLETON_MODE'] = 'true'
            os.environ['ELIZA_PID'] = str(os.getpid())
            os.environ['ELIZA_START_TIME'] = datetime.now().isoformat()
            
            # Import and run the component
            logger.info(f"📥 Importing component from: {component_path}")
            
            # Add the component directory to Python path
            component_dir = os.path.dirname(os.path.abspath(component_path))
            if component_dir not in sys.path:
                sys.path.insert(0, component_dir)
                
            # Execute the component
            logger.info("⚡ Executing Enhanced Eliza Central Component...")
            
            with open(component_path, 'r') as f:
                component_code = f.read()
                
            # Execute in controlled environment
            exec_globals = {
                '__name__': '__main__',
                '__file__': component_path,
                'SINGLETON_MODE': True,
                'SINGLETON_PID': os.getpid()
            }
            
            exec(component_code, exec_globals)
            
            logger.info("✅ Enhanced Eliza Central Component started successfully")
            self.is_running = True
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Eliza component: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            return False
            
    def monitor_instance(self):
        """Monitor the running instance"""
        logger.info("👁️ Starting instance monitoring...")
        
        while self.is_running:
            try:
                # Check if we're still the only instance
                current_instances = self.check_existing_instances()
                
                if len(current_instances) > 1:
                    logger.warning(f"⚠️ Multiple instances detected: {len(current_instances)}")
                    # Kill others, keep ourselves
                    for proc_info in current_instances:
                        if proc_info['pid'] != os.getpid():
                            try:
                                os.kill(proc_info['pid'], signal.SIGTERM)
                                logger.info(f"🔪 Terminated duplicate PID: {proc_info['pid']}")
                            except:
                                pass
                                
                # Update PID file timestamp
                if os.path.exists(self.pid_file):
                    try:
                        with open(self.pid_file, 'r') as f:
                            pid_info = json.load(f)
                        pid_info['last_heartbeat'] = datetime.now().isoformat()
                        with open(self.pid_file, 'w') as f:
                            json.dump(pid_info, f, indent=2)
                    except:
                        pass
                        
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(10)
                
    def cleanup_and_exit(self):
        """Clean shutdown"""
        logger.info("🛑 Initiating clean shutdown...")
        
        self.is_running = False
        self.remove_pid_lock()
        
        logger.info("✅ Clean shutdown completed")
        
    def run(self):
        """Main execution method"""
        logger.info("🚀 ELIZA SINGLETON MANAGER STARTED")
        logger.info("🎯 Mission: Ensure single Enhanced Eliza Central Component instance")
        
        try:
            # Check for existing valid lock
            if self.check_lock_validity():
                logger.error("❌ Another Eliza instance is already running")
                logger.info("🔪 Killing existing instances to start fresh...")
                self.kill_existing_instances()
                time.sleep(3)
                
            # Kill any existing instances
            killed = self.kill_existing_instances()
            if killed > 0:
                logger.info("⏳ Waiting for processes to fully terminate...")
                time.sleep(5)
                
            # Create our lock
            if not self.create_pid_lock():
                logger.error("❌ Failed to create PID lock")
                return False
                
            # Start the single instance
            if not self.start_single_eliza_instance():
                logger.error("❌ Failed to start Eliza instance")
                self.remove_pid_lock()
                return False
                
            # Start monitoring in background thread
            monitor_thread = threading.Thread(target=self.monitor_instance, daemon=True)
            monitor_thread.start()
            
            logger.info("✅ SINGLETON ELIZA MANAGER OPERATIONAL")
            logger.info("👁️ Monitoring for duplicate instances...")
            
            # Keep the main thread alive
            try:
                while self.is_running:
                    time.sleep(10)
            except KeyboardInterrupt:
                logger.info("👋 Received shutdown signal")
                
        except Exception as e:
            logger.error(f"❌ Singleton manager error: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
        finally:
            self.cleanup_and_exit()

def main():
    """Main entry point"""
    manager = ElizaSingletonManager()
    return manager.run()

if __name__ == "__main__":
    print("🚀 LAUNCHING ELIZA SINGLETON MANAGER...")
    print("🎯 Ensuring only ONE Enhanced Eliza Central Component runs")
    
    try:
        main()
    except KeyboardInterrupt:
        print("👋 Singleton manager shutdown requested")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        print("🏁 Singleton manager session completed")
