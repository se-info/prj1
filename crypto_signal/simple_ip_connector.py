#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple IP Connector - Connect to any IP address and port
Perfect for connecting to your local server on port 8000
"""

import socket
import requests
import time
import json


def get_local_ip():
    """Get your local IP address"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def check_connection(ip, port):
    """Check if you can connect to an IP and port"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, port))
        sock.close()

        if result == 0:
            print(f"✅ Connection successful to {ip}:{port}")
            return True
        else:
            print(f"❌ Cannot connect to {ip}:{port}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False


def make_http_request(ip, port, path="/"):
    """Make HTTP request to the IP and port"""
    try:
        url = f"http://{ip}:{port}{path}"
        print(f"🌐 Making HTTP request to: {url}")

        response = requests.get(url, timeout=10)

        print(f"✅ HTTP Response received:")
        print(f"   Status Code: {response.status_code}")
        print(
            f"   Content Type: {response.headers.get('content-type', 'Unknown')}")

        # Try to parse JSON response
        try:
            json_data = response.json()
            print(f"   JSON Response: {json.dumps(json_data, indent=2)}")
        except:
            print(f"   Text Response: {response.text[:200]}...")

        return True

    except Exception as e:
        print(f"❌ HTTP request failed: {e}")
        return False


def send_tcp_message(ip, port, message="Hello from crypto project!"):
    """Send a TCP message to the IP and port"""
    try:
        print(f"🔌 Sending TCP message to {ip}:{port}")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        sock.connect((ip, port))

        # Send message
        sock.send(message.encode('utf-8'))

        # Try to receive response
        try:
            response = sock.recv(1024).decode('utf-8')
            print(f"✅ TCP Response: {response}")
        except:
            print("✅ TCP message sent (no response)")

        sock.close()
        return True

    except Exception as e:
        print(f"❌ TCP connection failed: {e}")
        return False


def main():
    """Main function to test IP connections"""
    print("🌐 SIMPLE IP CONNECTOR")
    print("=" * 50)

    # Get your local IP
    local_ip = get_local_ip()
    print(f"🔍 Your local IP: {local_ip}")

    # Default settings for port 8000
    target_ip = local_ip  # Connect to your own machine
    target_port = 8000

    print(f"\n🎯 Target: {target_ip}:{target_port}")
    print("=" * 30)

    # Test 1: Basic connection check
    print("\n1️⃣ Testing basic connectivity...")
    if check_connection(target_ip, target_port):

        # Test 2: HTTP request
        print("\n2️⃣ Testing HTTP connection...")
        make_http_request(target_ip, target_port)

        # Test 3: TCP message
        print("\n3️⃣ Testing TCP connection...")
        send_tcp_message(target_ip, target_port)

    else:
        print(f"\n⚠️  Cannot connect to {target_ip}:{target_port}")
        print("💡 Possible solutions:")
        print("   1. Start a server on that port:")
        print(f"      python local_server_8000.py")
        print("   2. Check if firewall is blocking the connection")
        print("   3. Make sure the IP address is correct")

    # Also test some common services
    print(f"\n🔍 Testing other common connections:")
    print("-" * 40)

    # Test Google DNS
    print("Testing Google DNS (8.8.8.8:53)...")
    check_connection("8.8.8.8", 53)

    # Test Google HTTP
    print("Testing Google HTTP (google.com:80)...")
    try:
        response = requests.get("http://google.com", timeout=5)
        print(f"✅ Google HTTP: Status {response.status_code}")
    except:
        print("❌ Google HTTP: Failed")

    print(f"\n📱 Access from other devices:")
    print(f"   Open browser and go to: http://{local_ip}:8000")
    print(f"   (Make sure your server is running on port 8000)")


if __name__ == "__main__":
    main()
