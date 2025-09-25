#!/usr/bin/env python3
"""
Main Entry Point for Invoice AI System
======================================

This is the main application launcher that provides a unified interface
to start and manage all components of the Invoice AI system.

Usage:
    python main.py [command] [options]

Commands:
    start           Start all services (backend, chatbot, frontend)
    backend         Start only backend service
    chatbot         Start only chatbot service
    frontend        Start only frontend service (requires Node.js)
    stop            Stop all running services
    status          Check status of all services
    setup           Install dependencies and setup environment
    help            Show this help message

Examples:
    python main.py start           # Start all services
    python main.py backend         # Start only backend
    python main.py setup           # Setup dependencies
"""

import os
import sys
import subprocess
import time
import requests
import argparse
from pathlib import Path

class InvoiceAILauncher:
    def __init__(self):
        self.root_dir = Path(__file__).parent.absolute()
        self.backend_dir = self.root_dir / "backend"
        self.chatbot_dir = self.root_dir / "chatbot"
        self.frontend_dir = self.root_dir / "frontend"
        
        # Service configuration
        self.services = {
            'backend': {
                'port': 5000,
                'dir': self.backend_dir,
                'cmd': ['python', '-m', 'flask', 'run', '--host=0.0.0.0', '--port=5000'],
                'health_url': 'http://localhost:5000/api/health',
                'env_file': '.env'
            },
            'chatbot': {
                'port': 5001,
                'dir': self.chatbot_dir,
                'cmd': ['python', 'app.py'],
                'health_url': 'http://localhost:5001/health',
                'env_file': '.env'
            },
            'frontend': {
                'port': 5174,
                'dir': self.frontend_dir,
                'cmd': ['npm', 'run', 'dev'],
                'health_url': 'http://localhost:5174',
                'env_file': None
            }
        }
        
        self.processes = {}

    def print_banner(self):
        """Print application banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    Invoice AI System                         ║
║                  Main Application Launcher                   ║
╠══════════════════════════════════════════════════════════════╣
║  🚀 Backend API Server      - Port 5000                     ║
║  🤖 AI Chatbot Service      - Port 5001                     ║
║  🌐 Frontend Web App        - Port 5174                     ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def setup_environment(self):
        """Setup environment files and dependencies"""
        print("🔧 Setting up environment...")
        
        # Create backend .env
        backend_env = self.backend_dir / '.env'
        if not backend_env.exists():
            backend_env_content = """# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True

# Database Configuration
SQLALCHEMY_DATABASE_URI=sqlite:///invoice_ai.db
SQLALCHEMY_TRACK_MODIFICATIONS=False

# AI Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174
"""
            backend_env.write_text(backend_env_content)
            print(f"✅ Created {backend_env}")
        
        # Create chatbot .env
        chatbot_env = self.chatbot_dir / '.env'
        if not chatbot_env.exists():
            chatbot_env_content = """# Chatbot Configuration
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=True

# AI Configuration
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo

# Backend API
BACKEND_API_URL=http://localhost:5000

# Logging
LOG_LEVEL=INFO
"""
            chatbot_env.write_text(chatbot_env_content)
            print(f"✅ Created {chatbot_env}")

    def check_service_health(self, service_name, timeout=30):
        """Check if a service is healthy"""
        service = self.services[service_name]
        health_url = service['health_url']
        
        print(f"🔍 Checking {service_name} health at {health_url}...")
        
        for attempt in range(timeout):
            try:
                response = requests.get(health_url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {service_name.capitalize()} is healthy!")
                    return True
            except requests.exceptions.RequestException:
                if attempt == 0:
                    print(f"⏳ Waiting for {service_name} to start...")
                time.sleep(1)
        
        print(f"❌ {service_name.capitalize()} failed to start or is unhealthy")
        return False

    def start_service(self, service_name):
        """Start a specific service"""
        if service_name not in self.services:
            print(f"❌ Unknown service: {service_name}")
            return False
        
        service = self.services[service_name]
        service_dir = service['dir']
        
        if not service_dir.exists():
            print(f"❌ Service directory not found: {service_dir}")
            return False
        
        print(f"🚀 Starting {service_name} on port {service['port']}...")
        
        try:
            # Change to service directory and start
            env = os.environ.copy()
            if service['env_file']:
                env_file = service_dir / service['env_file']
                if env_file.exists():
                    # Load environment variables from .env file
                    with open(env_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                env[key.strip()] = value.strip()
            
            process = subprocess.Popen(
                service['cmd'],
                cwd=service_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.processes[service_name] = process
            print(f"✅ {service_name.capitalize()} started with PID {process.pid}")
            
            # Give service time to start
            time.sleep(3)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {service_name}: {e}")
            return False

    def stop_service(self, service_name):
        """Stop a specific service"""
        if service_name in self.processes:
            process = self.processes[service_name]
            if process.poll() is None:  # Process is still running
                print(f"🛑 Stopping {service_name}...")
                process.terminate()
                try:
                    process.wait(timeout=10)
                    print(f"✅ {service_name.capitalize()} stopped")
                except subprocess.TimeoutExpired:
                    process.kill()
                    print(f"🔪 Force killed {service_name}")
                del self.processes[service_name]
            else:
                print(f"ℹ️  {service_name.capitalize()} already stopped")
        else:
            print(f"ℹ️  {service_name.capitalize()} not running")

    def stop_all_services(self):
        """Stop all running services"""
        print("🛑 Stopping all services...")
        for service_name in list(self.processes.keys()):
            self.stop_service(service_name)

    def start_all_services(self):
        """Start all services"""
        print("🚀 Starting all services...")
        
        # Start backend first
        if self.start_service('backend'):
            self.check_service_health('backend')
        
        # Then chatbot
        if self.start_service('chatbot'):
            self.check_service_health('chatbot')
        
        # Finally frontend
        if self.start_service('frontend'):
            time.sleep(5)  # Frontend takes longer to start
            self.check_service_health('frontend')
        
        print("\n🎉 All services started!")
        print("🌐 Access your application:")
        print("   Frontend:  http://localhost:5174")
        print("   Backend:   http://localhost:5000")
        print("   Chatbot:   http://localhost:5001")
        print("\n💡 Press Ctrl+C to stop all services")
        
        try:
            # Keep main process running
            while True:
                time.sleep(1)
                # Check if any process died
                for service_name, process in list(self.processes.items()):
                    if process.poll() is not None:
                        print(f"⚠️  {service_name.capitalize()} stopped unexpectedly")
                        del self.processes[service_name]
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal...")
            self.stop_all_services()

    def show_status(self):
        """Show status of all services"""
        print("📊 Service Status:")
        print("=" * 50)
        
        for service_name, service in self.services.items():
            port = service['port']
            try:
                response = requests.get(service['health_url'], timeout=2)
                if response.status_code == 200:
                    status = "🟢 RUNNING"
                else:
                    status = f"🟡 UNHEALTHY (HTTP {response.status_code})"
            except requests.exceptions.RequestException:
                status = "🔴 STOPPED"
            
            print(f"{service_name.capitalize():12} (Port {port}): {status}")

def main():
    launcher = InvoiceAILauncher()
    
    parser = argparse.ArgumentParser(description='Invoice AI System Launcher')
    parser.add_argument('command', nargs='?', default='help',
                      choices=['start', 'backend', 'chatbot', 'frontend', 'stop', 'status', 'setup', 'help'],
                      help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'help':
        launcher.print_banner()
        parser.print_help()
        return
    
    launcher.print_banner()
    
    if args.command == 'setup':
        launcher.setup_environment()
        print("✅ Setup complete! Run 'python main.py start' to launch all services")
    
    elif args.command == 'start':
        launcher.setup_environment()
        launcher.start_all_services()
    
    elif args.command in ['backend', 'chatbot', 'frontend']:
        launcher.setup_environment()
        launcher.start_service(args.command)
        
        # Keep single service running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n🛑 Stopping {args.command}...")
            launcher.stop_service(args.command)
    
    elif args.command == 'stop':
        launcher.stop_all_services()
    
    elif args.command == 'status':
        launcher.show_status()

if __name__ == "__main__":
    main()