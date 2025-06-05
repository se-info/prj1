#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP Connection Examples - Various methods to connect to IP addresses in Python
Suitable for crypto trading apps, API connections, and network communication
"""

import socket
import requests
import urllib3
import asyncio
import aiohttp
import telnetlib
import subprocess
import paramiko
import time
from typing import Optional, Tuple, Dict, Any
import json


class IPConnectionManager:
    """Class to handle various types of IP connections"""

    def __init__(self):
        self.session = requests.Session()
        self.timeout = 30

    # ========================================
    # 1. BASIC TCP SOCKET CONNECTION
    # ========================================

    def tcp_connect(self, ip: str, port: int, message: str = "Hello") -> Tuple[bool, str]:
        """
        Basic TCP socket connection
        Usage: For connecting to trading APIs, database servers, etc.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            # Connect to the IP and port
            result = sock.connect_ex((ip, port))

            if result == 0:
                # Connection successful
                sock.send(message.encode('utf-8'))
                response = sock.recv(1024).decode('utf-8')
                sock.close()
                return True, f"Connected successfully. Response: {response}"
            else:
                sock.close()
                return False, f"Connection failed. Error code: {result}"

        except Exception as e:
            return False, f"TCP connection error: {str(e)}"

    def check_port_open(self, ip: str, port: int) -> bool:
        """Check if a specific port is open on the IP"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False

    # ========================================
    # 2. UDP CONNECTION
    # ========================================

    def udp_connect(self, ip: str, port: int, message: str = "Hello UDP") -> Tuple[bool, str]:
        """
        UDP socket connection (connectionless)
        Usage: For real-time data feeds, broadcasting
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)

            # Send message
            sock.sendto(message.encode('utf-8'), (ip, port))

            # Try to receive response
            try:
                response, addr = sock.recvfrom(1024)
                sock.close()
                return True, f"UDP message sent and response received: {response.decode('utf-8')}"
            except socket.timeout:
                sock.close()
                return True, "UDP message sent (no response expected/received)"

        except Exception as e:
            return False, f"UDP connection error: {str(e)}"

    # ========================================
    # 3. HTTP/HTTPS REQUESTS
    # ========================================

    def http_connect(self, ip: str, port: int = 80, path: str = "/",
                     method: str = "GET", data: Dict = None,
                     headers: Dict = None, use_https: bool = False) -> Tuple[bool, Dict]:
        """
        HTTP/HTTPS connection using requests
        Usage: For API calls to crypto exchanges, web services
        """
        try:
            protocol = "https" if use_https else "http"
            url = f"{protocol}://{ip}:{port}{path}"

            default_headers = {
                'User-Agent': 'CryptoApp/1.0',
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }

            if headers:
                default_headers.update(headers)

            if method.upper() == "GET":
                response = self.session.get(url, headers=default_headers,
                                            timeout=self.timeout, params=data)
            elif method.upper() == "POST":
                response = self.session.post(url, headers=default_headers,
                                             timeout=self.timeout, json=data)
            elif method.upper() == "PUT":
                response = self.session.put(url, headers=default_headers,
                                            timeout=self.timeout, json=data)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=default_headers,
                                               timeout=self.timeout)

            return True, {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'content': response.text,
                'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
            }

        except Exception as e:
            return False, {'error': str(e)}

    # ========================================
    # 4. ASYNC HTTP CONNECTION
    # ========================================

    async def async_http_connect(self, ip: str, port: int = 80, path: str = "/",
                                 method: str = "GET", data: Dict = None,
                                 use_https: bool = False) -> Tuple[bool, Dict]:
        """
        Asynchronous HTTP connection
        Usage: For high-performance concurrent API calls
        """
        try:
            protocol = "https" if use_https else "http"
            url = f"{protocol}://{ip}:{port}{path}"

            async with aiohttp.ClientSession() as session:
                async with session.request(method, url, json=data,
                                           timeout=aiohttp.ClientTimeout(total=self.timeout)) as response:
                    content = await response.text()
                    try:
                        json_content = await response.json()
                    except:
                        json_content = None

                    return True, {
                        'status_code': response.status,
                        'headers': dict(response.headers),
                        'content': content,
                        'json': json_content
                    }

        except Exception as e:
            return False, {'error': str(e)}

    # ========================================
    # 5. TELNET CONNECTION
    # ========================================

    def telnet_connect(self, ip: str, port: int = 23, commands: list = None) -> Tuple[bool, str]:
        """
        Telnet connection
        Usage: For connecting to network devices, servers with telnet access
        """
        try:
            tn = telnetlib.Telnet(ip, port, timeout=self.timeout)

            output = ""
            if commands:
                for command in commands:
                    tn.write(command.encode('ascii') + b"\n")
                    time.sleep(1)
                    output += tn.read_very_eager().decode('ascii')

            tn.close()
            return True, f"Telnet connection successful. Output: {output}"

        except Exception as e:
            return False, f"Telnet connection error: {str(e)}"

    # ========================================
    # 6. SSH CONNECTION
    # ========================================

    def ssh_connect(self, ip: str, username: str, password: str = None,
                    key_file: str = None, port: int = 22,
                    commands: list = None) -> Tuple[bool, str]:
        """
        SSH connection using paramiko
        Usage: For secure remote server management
        """
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if key_file:
                ssh.connect(ip, port=port, username=username,
                            key_filename=key_file, timeout=self.timeout)
            else:
                ssh.connect(ip, port=port, username=username,
                            password=password, timeout=self.timeout)

            output = ""
            if commands:
                for command in commands:
                    stdin, stdout, stderr = ssh.exec_command(command)
                    output += f"Command: {command}\n"
                    output += f"Output: {stdout.read().decode()}\n"
                    output += f"Error: {stderr.read().decode()}\n"

            ssh.close()
            return True, f"SSH connection successful. Output: {output}"

        except Exception as e:
            return False, f"SSH connection error: {str(e)}"

    # ========================================
    # 7. PING TEST
    # ========================================

    def ping_test(self, ip: str, count: int = 4) -> Tuple[bool, str]:
        """
        Ping test to check if IP is reachable
        Usage: For network connectivity testing
        """
        try:
            import platform
            system = platform.system().lower()

            if system == "windows":
                cmd = f"ping -n {count} {ip}"
            else:
                cmd = f"ping -c {count} {ip}"

            result = subprocess.run(
                cmd.split(), capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return True, f"Ping successful:\n{result.stdout}"
            else:
                return False, f"Ping failed:\n{result.stderr}"

        except Exception as e:
            return False, f"Ping error: {str(e)}"

    # ========================================
    # 8. NETWORK SCAN
    # ========================================

    def scan_ports(self, ip: str, ports: list) -> Dict[int, bool]:
        """
        Scan multiple ports on an IP
        Usage: For network discovery and security assessment
        """
        results = {}
        for port in ports:
            results[port] = self.check_port_open(ip, port)
        return results

    def scan_subnet(self, subnet: str, port: int = 80) -> Dict[str, bool]:
        """
        Scan a subnet for active IPs
        Usage: For network discovery
        Example: scan_subnet("192.168.1", 80) scans 192.168.1.1-254
        """
        active_ips = {}
        for i in range(1, 255):
            ip = f"{subnet}.{i}"
            active_ips[ip] = self.check_port_open(ip, port)
        return active_ips


# ========================================
# USAGE EXAMPLES AND DEMO FUNCTIONS
# ========================================

def demo_crypto_api_connection():
    """Demo: Connect to cryptocurrency exchange APIs"""
    conn = IPConnectionManager()

    print("🔗 Testing Crypto Exchange API Connections:")
    print("=" * 50)

    # Test Binance API
    success, result = conn.http_connect(
        ip="api.binance.com",
        port=443,
        path="/api/v3/ticker/price?symbol=BTCUSDT",
        use_https=True
    )

    if success:
        print("✅ Binance API Connection Successful")
        if result.get('json'):
            print(f"   BTC Price: {result['json'].get('price', 'N/A')}")
    else:
        print(f"❌ Binance API Connection Failed: {result}")


def demo_local_server_connection():
    """Demo: Connect to local server on port 8000"""
    conn = IPConnectionManager()

    print("\n🌐 Testing Local Server Connection (Port 8000):")
    print("=" * 50)

    # Get local IP (from your existing script)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        print(f"🔍 Local IP detected: {local_ip}")

        # Test 1: Check if port 8000 is open
        print(f"\n📡 Checking if port 8000 is open...")
        is_open = conn.check_port_open(local_ip, 8000)
        print(f"   Port 8000 status: {'✅ OPEN' if is_open else '❌ CLOSED'}")

        if not is_open:
            print("⚠️  Port 8000 is not open. Please start the server first:")
            print(f"   python local_server_8000.py")
            return

        # Test 2: HTTP GET request
        print(f"\n🌐 Testing HTTP GET request...")
        success, result = conn.http_connect(
            ip=local_ip,
            port=8000,
            path="/",
            method="GET",
            use_https=False
        )

        if success:
            print(f"✅ GET Request Successful")
            print(f"   URL: http://{local_ip}:8000")
            print(f"   Status Code: {result['status_code']}")
            if result.get('json'):
                print(f"   Response: {result['json']['message']}")
        else:
            print(f"❌ GET Request Failed: {result}")

        # Test 3: HTTP POST request with data
        print(f"\n📤 Testing HTTP POST request...")
        test_data = {
            "test_message": "Hello from crypto project!",
            "timestamp": str(time.time()),
            "source": "ip_connection_examples.py"
        }

        success, result = conn.http_connect(
            ip=local_ip,
            port=8000,
            path="/api/test",
            method="POST",
            data=test_data,
            use_https=False
        )

        if success:
            print(f"✅ POST Request Successful")
            print(f"   Status Code: {result['status_code']}")
            if result.get('json'):
                print(f"   Response: {result['json']['message']}")
        else:
            print(f"❌ POST Request Failed: {result}")

        # Test 4: TCP Socket connection
        print(f"\n🔌 Testing TCP Socket connection...")
        success, result = conn.tcp_connect(
            local_ip, 8000, "Hello TCP from crypto project!")
        if success:
            print(f"✅ TCP Connection: {result}")
        else:
            print(f"❌ TCP Connection Failed: {result}")

    except Exception as e:
        print(f"❌ Error getting local IP: {e}")


async def demo_async_connections():
    """Demo: Asynchronous connections for better performance"""
    conn = IPConnectionManager()

    print("\n⚡ Testing Async HTTP Connections:")
    print("=" * 50)

    # Multiple concurrent API calls
    tasks = [
        conn.async_http_connect("httpbin.org", 443, "/json", use_https=True),
        conn.async_http_connect("api.github.com", 443,
                                "/users/octocat", use_https=True),
        conn.async_http_connect(
            "jsonplaceholder.typicode.com", 443, "/posts/1", use_https=True)
    ]

    results = await asyncio.gather(*tasks)

    for i, (success, result) in enumerate(results):
        if success:
            print(f"✅ Async Connection {i+1} Successful")
        else:
            print(f"❌ Async Connection {i+1} Failed: {result}")


def demo_network_scanning():
    """Demo: Network scanning capabilities"""
    conn = IPConnectionManager()

    print("\n🔍 Network Scanning Demo:")
    print("=" * 50)

    # Common ports to scan
    common_ports = [22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5000]

    # Test local machine
    results = conn.scan_ports("127.0.0.1", common_ports)

    print("Port scan results for localhost:")
    for port, is_open in results.items():
        status = "OPEN" if is_open else "CLOSED"
        print(f"   Port {port}: {status}")


def main():
    """Main demonstration function"""
    print("🌐 IP CONNECTION EXAMPLES FOR CRYPTO PROJECT")
    print("=" * 60)

    # Initialize connection manager
    conn = IPConnectionManager()

    # Demo 1: Basic connectivity test
    print("\n📡 Basic Connectivity Tests:")
    print("-" * 40)

    # Ping test
    success, result = conn.ping_test("8.8.8.8", 2)
    print(f"Ping 8.8.8.8: {'✅ Success' if success else '❌ Failed'}")

    # Port check
    is_open = conn.check_port_open("google.com", 80)
    print(f"Google.com:80: {'✅ Open' if is_open else '❌ Closed'}")

    # Demo 2: HTTP connections
    demo_crypto_api_connection()
    demo_local_server_connection()

    # Demo 3: Network scanning
    demo_network_scanning()

    # Demo 4: Async connections (if event loop available)
    try:
        print("\n⚡ Running Async Demo...")
        asyncio.run(demo_async_connections())
    except Exception as e:
        print(f"❌ Async demo failed: {e}")

    print("\n✅ All demos completed!")
    print("\n💡 Integration Tips:")
    print("- Use HTTP connections for crypto exchange APIs")
    print("- Use TCP sockets for real-time data streams")
    print("- Use async connections for high-performance trading")
    print("- Use network scanning for discovering services")


if __name__ == "__main__":
    main()
