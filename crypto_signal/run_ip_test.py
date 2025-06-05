#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run IP Connection Tests - Start server and test connections
"""

import subprocess
import threading
import time
import socket
import sys
import os


def get_local_ip():
    """Get local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def check_port_open(ip, port, timeout=5):
    """Check if port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False


def start_server_background():
    """Start the server in background"""
    try:
        print("🚀 Starting HTTP server on port 8000...")
        process = subprocess.Popen([
            sys.executable, "local_server_8000.py"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Wait a moment for server to start
        time.sleep(3)

        # Check if server is running
        local_ip = get_local_ip()
        if check_port_open(local_ip, 8000):
            print(f"✅ Server started successfully on {local_ip}:8000")
            return process
        else:
            print("❌ Server failed to start properly")
            process.terminate()
            return None

    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None


def run_connection_tests():
    """Run the IP connection tests"""
    try:
        print("\n🧪 Running IP connection tests...")
        result = subprocess.run([
            sys.executable, "ip_connection_examples.py"
        ], capture_output=True, text=True)

        print("📊 TEST RESULTS:")
        print("=" * 50)
        print(result.stdout)

        if result.stderr:
            print("⚠️ ERRORS/WARNINGS:")
            print(result.stderr)

    except Exception as e:
        print(f"❌ Error running tests: {e}")


def main():
    """Main function to coordinate server and tests"""
    print("🌐 IP CONNECTION TEST RUNNER")
    print("=" * 60)

    local_ip = get_local_ip()
    print(f"🔍 Local IP: {local_ip}")

    # Check if port 8000 is already in use
    if check_port_open(local_ip, 8000):
        print("ℹ️  Port 8000 is already in use")
        print("🧪 Running tests against existing server...")
        run_connection_tests()
        return

    # Start server in background
    server_process = start_server_background()

    if server_process is None:
        print("❌ Cannot start server. Exiting...")
        return

    try:
        # Run connection tests
        run_connection_tests()

        print("\n✅ All tests completed!")
        print(f"🌐 Server still running at http://{local_ip}:8000")
        print("📱 You can access it from other devices on your network")
        print("\nPress Ctrl+C to stop the server...")

        # Keep server running until user stops it
        server_process.wait()

    except KeyboardInterrupt:
        print("\n\n🛑 Stopping server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped")

    except Exception as e:
        print(f"❌ Error during execution: {e}")
        if server_process:
            server_process.terminate()


if __name__ == "__main__":
    main()
