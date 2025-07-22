#!/usr/bin/env python3
"""
Dashboard Debug Runner
======================

Script for iterative debugging of the LULC Dashboard.
Monitors Streamlit output for errors and provides debugging information.

Author: Dashboard Iniciativas LULC
Date: 2025
"""

import subprocess
import sys
import time
import re
import threading
from typing import List, Dict, Optional


class StreamlitDebugger:
    """Interactive Streamlit debugger for catching and analyzing errors."""
    
    def __init__(self, port: int = 8503):
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        self.errors: List[Dict] = []
        self.running = False
        
    def start_streamlit(self) -> bool:
        """Start Streamlit with debugging enabled."""
        try:
            cmd = [
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.port", str(self.port),
                "--server.fileWatcherType", "auto",
                "--server.runOnSave", "true",
                "--client.toolbarMode", "developer",
                "--server.allowRunOnSave", "true",
                "--logger.level", "debug"
            ]
            
            print(f"🚀 Starting Streamlit on port {self.port}...")
            print(f"📱 Dashboard URL: http://localhost:{self.port}")
            
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.running = True
            return True
            
        except Exception as e:
            print(f"❌ Failed to start Streamlit: {e}")
            return False
    
    def monitor_output(self):
        """Monitor Streamlit output for errors."""
        if not self.process or not self.process.stdout:
            return
            
        error_pattern = re.compile(r'Uncaught app execution|Traceback|NameError|ImportError|AttributeError')
        
        for line in iter(self.process.stdout.readline, ''):
            if not self.running:
                break
                
            line = line.strip()
            if line:
                print(line)
                
                # Check for errors
                if error_pattern.search(line):
                    self.capture_error(line)
                    
                # Check if app is ready
                if "You can now view your Streamlit app" in line:
                    print("\n✅ Dashboard is ready!")
                    print(f"🔗 Open: http://localhost:{self.port}")
    
    def capture_error(self, error_line: str):
        """Capture and analyze errors."""
        error_info = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'error': error_line,
            'type': self.classify_error(error_line)
        }
        
        self.errors.append(error_info)
        
        print("\n🔥 ERROR DETECTED:")
        print(f"   Type: {error_info['type']}")
        print(f"   Time: {error_info['timestamp']}")
        print(f"   Error: {error_line}")
        
        # Provide suggestions based on error type
        self.suggest_fix(error_info['type'])
    
    def classify_error(self, error_line: str) -> str:
        """Classify the type of error."""
        if "NameError" in error_line:
            return "NameError"
        elif "ImportError" in error_line or "ModuleNotFoundError" in error_line:
            return "ImportError"
        elif "AttributeError" in error_line:
            return "AttributeError"
        elif "TypeError" in error_line:
            return "TypeError"
        elif "ValueError" in error_line:
            return "ValueError"
        else:
            return "Unknown"
    
    def suggest_fix(self, error_type: str):
        """Suggest fixes based on error type."""
        suggestions = {
            "NameError": "❓ Variable or function not defined. Check spelling and imports.",
            "ImportError": "📦 Module not found. Check if package is installed: pip install <package>",
            "AttributeError": "🔍 Object doesn't have expected attribute. Check object type.",
            "TypeError": "🔧 Type mismatch. Check function parameters and types.",
            "ValueError": "📊 Invalid value. Check data format and ranges."
        }
        
        suggestion = suggestions.get(error_type, "🤔 Unknown error type. Check the full traceback.")
        print(f"   💡 Suggestion: {suggestion}")
    
    def stop(self):
        """Stop the Streamlit process."""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()
            print("\n🛑 Streamlit stopped.")
    
    def run_interactive(self):
        """Run interactive debugging session."""
        if not self.start_streamlit():
            return
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=self.monitor_output)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            print("\n" + "="*60)
            print("🔧 INTERACTIVE DEBUG MODE")
            print("="*60)
            print("Commands:")
            print("  'status' - Show current status")
            print("  'errors' - Show captured errors")
            print("  'clear'  - Clear error log")
            print("  'quit'   - Stop debugging")
            print("="*60)
            
            while self.running:
                try:
                    command = input("\n🔧 Debug> ").strip().lower()
                    
                    if command == 'quit' or command == 'q':
                        break
                    elif command == 'status':
                        self.show_status()
                    elif command == 'errors':
                        self.show_errors()
                    elif command == 'clear':
                        self.errors.clear()
                        print("✅ Error log cleared.")
                    elif command == 'help' or command == 'h':
                        self.show_help()
                    elif command:
                        print(f"❓ Unknown command: {command}. Type 'help' for available commands.")
                        
                except KeyboardInterrupt:
                    break
                    
        finally:
            self.stop()
    
    def show_status(self):
        """Show current debugging status."""
        print("\n📊 DEBUG STATUS:")
        print(f"   Port: {self.port}")
        print(f"   Running: {'✅ Yes' if self.running else '❌ No'}")
        print(f"   Errors captured: {len(self.errors)}")
        print(f"   URL: http://localhost:{self.port}")
    
    def show_errors(self):
        """Show captured errors."""
        if not self.errors:
            print("✅ No errors captured yet!")
            return
            
        print(f"\n🔥 CAPTURED ERRORS ({len(self.errors)}):")
        print("-" * 50)
        
        for i, error in enumerate(self.errors[-10:], 1):  # Show last 10 errors
            print(f"{i}. [{error['timestamp']}] {error['type']}")
            print(f"   {error['error']}")
        
        if len(self.errors) > 10:
            print(f"   ... and {len(self.errors) - 10} more errors")
    
    def show_help(self):
        """Show help information."""
        print("\n📚 HELP:")
        print("   status  - Show debugging status")
        print("   errors  - Show captured errors")
        print("   clear   - Clear error log")
        print("   help    - Show this help")
        print("   quit    - Stop debugging and exit")


def main():
    """Main debugging function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="LULC Dashboard Interactive Debugger")
    parser.add_argument("--port", type=int, default=8503, help="Port for Streamlit (default: 8503)")
    parser.add_argument("--monitor-only", action="store_true", help="Only monitor, don't start interactive mode")
    
    args = parser.parse_args()
    
    debugger = StreamlitDebugger(port=args.port)
    
    if args.monitor_only:
        # Just start and monitor
        if debugger.start_streamlit():
            try:
                debugger.monitor_output()
            except KeyboardInterrupt:
                debugger.stop()
    else:
        # Interactive mode
        debugger.run_interactive()


if __name__ == "__main__":
    main()
