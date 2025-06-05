#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Local HTTP Server for Port 8000 - Testing IP Connections
Simple server to test IP connection examples
"""

import socket
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time


class SimpleHTTPHandler(BaseHTTPRequestHandler):
    """Custom HTTP handler for our test server"""

    def do_GET(self):
        """Handle GET requests"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Create response data
        response_data = {
            'status': 'success',
            'message': 'Connection successful to local server',
            'timestamp': datetime.now().isoformat(),
            'client_ip': self.client_address[0],
            'path': self.path,
            'method': 'GET',
            'server_port': 8000
        }

        self.wfile.write(json.dumps(response_data, indent=2).encode())

    def do_POST(self):
        """Handle POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        try:
            received_data = json.loads(post_data.decode()) if post_data else {}
        except:
            received_data = {}

        response_data = {
            'status': 'success',
            'message': 'POST request received successfully',
            'timestamp': datetime.now().isoformat(),
            'client_ip': self.client_address[0],
            'received_data': received_data,
            'method': 'POST',
            'server_port': 8000
        }

        self.wfile.write(json.dumps(response_data, indent=2).encode())

    def log_message(self, format, *args):
        """Custom log message format"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


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


def start_server(ip="0.0.0.0", port=8000):
    """Start the HTTP server"""
    server_address = (ip, port)
    httpd = HTTPServer(server_address, SimpleHTTPHandler)

    local_ip = get_local_ip()

    print("🚀 LOCAL HTTP SERVER STARTING")
    print("=" * 50)
    print(f"📍 Server running on: {ip}:{port}")
    print(f"🌐 Local IP: {local_ip}")
    print(f"🔗 Access URLs:")
    print(f"   - Local: http://127.0.0.1:{port}")
    print(f"   - Network: http://{local_ip}:{port}")
    print("=" * 50)
    print("📊 Server ready to receive connections...")
    print("Press Ctrl+C to stop the server")
    print()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopping...")
        httpd.shutdown()
        print("✅ Server stopped successfully")


if __name__ == "__main__":
    start_server()
