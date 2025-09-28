#!/usr/bin/env python3
"""
Knowledge Research Assistant - Server Manager
==============================================
A simple utility to manage the Node.js server for the Knowledge Research App.

Usage:
    python manage.py start    - Start the server
    python manage.py stop     - Stop the server
    python manage.py restart  - Restart the server
    python manage.py status   - Check server status
"""

import subprocess
import sys
import time
import psutil
import requests
import os
from pathlib import Path

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header():
    """Print a nice header for the application"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}   🧠 Knowledge Research Assistant - Server Manager{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════{Colors.END}\n")

def check_node_installed():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"{Colors.GREEN}✓ Node.js is installed: {result.stdout.strip()}{Colors.END}")
            return True
    except FileNotFoundError:
        pass
    print(f"{Colors.RED}✗ Node.js is not installed. Please install it first.{Colors.END}")
    return False

def check_dependencies():
    """Check if npm dependencies are installed"""
    if not os.path.exists('node_modules'):
        print(f"{Colors.YELLOW}⚠ Dependencies not installed. Installing now...{Colors.END}")
        subprocess.run(['npm', 'install'], check=True)
        print(f"{Colors.GREEN}✓ Dependencies installed successfully{Colors.END}")
    else:
        print(f"{Colors.GREEN}✓ Dependencies are installed{Colors.END}")

def check_env_file():
    """Check if .env file exists and has API keys"""
    env_path = Path('.env')
    if not env_path.exists():
        print(f"{Colors.YELLOW}⚠ .env file not found!{Colors.END}")
        print(f"\n{Colors.BOLD}Creating .env file from template...{Colors.END}")
        
        template_content = """# Get your API keys from:
# Anthropic: https://console.anthropic.com/account/keys
# Perplexity: https://www.perplexity.ai/settings/api

CLAUDE_API_KEY=YOUR_ANTHROPIC_API_KEY_HERE
PERPLEXITY_API_KEY=YOUR_PERPLEXITY_API_KEY_HERE
PORT=3000
"""
        with open('.env', 'w') as f:
            f.write(template_content)
        
        print(f"{Colors.YELLOW}⚠ Please update .env with your actual API keys:{Colors.END}")
        print(f"   1. Claude/Anthropic API key (starts with 'sk-ant-api03-...')")
        print(f"   2. Perplexity API key (starts with 'pplx-...')")
        return False
    else:
        # Check if API keys are placeholder values
        with open('.env', 'r') as f:
            content = f.read()
            if 'YOUR_' in content or 'sk-proj-' in content or content.count('pplx-') == 1:
                print(f"{Colors.YELLOW}⚠ API keys need to be updated in .env file{Colors.END}")
                print(f"   • Claude key should start with 'sk-ant-api03-...'")
                print(f"   • Perplexity key should start with 'pplx-...'")
                return False
        print(f"{Colors.GREEN}✓ .env file exists{Colors.END}")
        return True

def find_node_processes():
    """Find all Node.js processes running server.js"""
    node_pids = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'node' in proc.info['name'].lower():
                if proc.info['cmdline'] and any('server.js' in cmd for cmd in proc.info['cmdline']):
                    node_pids.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return node_pids

def is_server_running():
    """Check if the server is running"""
    try:
        response = requests.get('http://localhost:3000/api/load-files', timeout=2)
        return response.status_code == 200
    except:
        return False

def start_server():
    """Start the Node.js server"""
    print(f"{Colors.BOLD}Starting server...{Colors.END}")
    
    if is_server_running():
        print(f"{Colors.YELLOW}⚠ Server is already running!{Colors.END}")
        print(f"📍 Access it at: {Colors.CYAN}http://localhost:3000{Colors.END}")
        return
    
    # Check prerequisites
    if not check_node_installed():
        return
    
    check_dependencies()
    has_valid_env = check_env_file()
    
    # Start the server
    if sys.platform == 'win32':
        # Windows: Use START command to open in new window
        subprocess.Popen('start cmd /k npm start', shell=True)
    else:
        # Unix/Mac: Run in background
        subprocess.Popen(['npm', 'start'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print(f"\n{Colors.BOLD}Waiting for server to start...{Colors.END}")
    
    # Wait for server to be ready
    for i in range(10):
        time.sleep(1)
        if is_server_running():
            print(f"\n{Colors.GREEN}✅ Server started successfully!{Colors.END}")
            print(f"\n📍 Access the application at: {Colors.CYAN}{Colors.BOLD}http://localhost:3000{Colors.END}")
            
            if not has_valid_env:
                print(f"\n{Colors.YELLOW}⚠ Remember to update your API keys in the .env file!{Colors.END}")
            
            print(f"\n{Colors.BOLD}Features available:{Colors.END}")
            print(f"   • View and approve Target and Knowledge documents")
            print(f"   • Generate research questions with Claude AI")
            print(f"   • Deep research with Perplexity Sonar")
            print(f"   • Automatic knowledge base integration")
            print(f"   • Persistent knowledge updates")
            return
    
    print(f"{Colors.RED}✗ Server failed to start. Check the console for errors.{Colors.END}")

def stop_server():
    """Stop all Node.js server processes"""
    print(f"{Colors.BOLD}Stopping server...{Colors.END}")
    
    pids = find_node_processes()
    if not pids:
        print(f"{Colors.YELLOW}⚠ No server processes found running{Colors.END}")
        return
    
    for pid in pids:
        try:
            proc = psutil.Process(pid)
            proc.terminate()
            print(f"{Colors.GREEN}✓ Stopped process {pid}{Colors.END}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            print(f"{Colors.YELLOW}⚠ Could not stop process {pid}{Colors.END}")
    
    time.sleep(1)
    
    if not is_server_running():
        print(f"{Colors.GREEN}✅ Server stopped successfully{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ Server may still be running. Try 'python manage.py stop' again.{Colors.END}")

def restart_server():
    """Restart the server"""
    print(f"{Colors.BOLD}Restarting server...{Colors.END}\n")
    stop_server()
    time.sleep(2)
    print("")
    start_server()

def check_status():
    """Check the server status"""
    print(f"{Colors.BOLD}Checking server status...{Colors.END}\n")
    
    if is_server_running():
        print(f"{Colors.GREEN}✅ Server is running{Colors.END}")
        print(f"📍 Access at: {Colors.CYAN}http://localhost:3000{Colors.END}")
        
        pids = find_node_processes()
        if pids:
            print(f"\n{Colors.BOLD}Process IDs:{Colors.END} {', '.join(map(str, pids))}")
    else:
        print(f"{Colors.YELLOW}⚠ Server is not running{Colors.END}")
        print(f"Start it with: {Colors.CYAN}python manage.py start{Colors.END}")

def show_help():
    """Show help information"""
    print(__doc__)
    print(f"\n{Colors.BOLD}Commands:{Colors.END}")
    print(f"  {Colors.CYAN}python manage.py start{Colors.END}    - Start the server")
    print(f"  {Colors.CYAN}python manage.py stop{Colors.END}     - Stop the server")
    print(f"  {Colors.CYAN}python manage.py restart{Colors.END}  - Restart the server")
    print(f"  {Colors.CYAN}python manage.py status{Colors.END}   - Check if server is running")
    print(f"  {Colors.CYAN}python manage.py help{Colors.END}     - Show this help message")

def main():
    """Main entry point"""
    print_header()
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    commands = {
        'start': start_server,
        'stop': stop_server,
        'restart': restart_server,
        'status': check_status,
        'help': show_help,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"{Colors.RED}✗ Unknown command: {command}{Colors.END}")
        show_help()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        sys.exit(1)



