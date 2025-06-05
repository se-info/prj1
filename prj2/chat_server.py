#!/usr/bin/env python3
"""
Local Network Chat Room Server
Handles multiple client connections, message broadcasting, and logging.
"""

import socket
import threading
import json
import datetime
import os
import base64
from typing import Dict, List, Set


class ChatServer:
    def __init__(self, host='0.0.0.0', port=5000, debug=True):
        self.host = host
        self.port = port
        self.debug = debug
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Client management
        self.clients: Dict[socket.socket, str] = {}  # socket -> nickname
        self.nicknames: Set[str] = set()  # active nicknames
        self.lock = threading.Lock()

        # Logging
        self.log_dir = "chat_logs"
        self.ensure_log_directory()

    def ensure_log_directory(self):
        """Create log directory if it doesn't exist."""
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

    def get_log_filename(self):
        """Generate log filename with current date."""
        today = datetime.datetime.now().strftime("%Y%m%d")
        return os.path.join(self.log_dir, f"chat_log_{today}.txt")

    def log_event(self, message):
        """Log an event to the daily log file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"

        # Print to console if debug mode is enabled
        if self.debug:
            print(f"DEBUG: {log_entry.strip()}")

        try:
            with open(self.get_log_filename(), "a", encoding="utf-8") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Logging error: {e}")

    def broadcast_message(self, message, sender_socket=None):
        """Broadcast a message to all connected clients except the sender."""
        message_json = json.dumps(message) + '\n'

        with self.lock:
            disconnected_clients = []

            for client_socket in self.clients:
                if client_socket != sender_socket:
                    try:
                        client_socket.send(message_json.encode('utf-8'))
                    except:
                        disconnected_clients.append(client_socket)

            # Remove disconnected clients
            for client in disconnected_clients:
                self.disconnect_client(client)

    def send_user_list(self):
        """Send updated user list to all clients."""
        with self.lock:
            user_list = list(self.nicknames)

        message = {
            "type": "user_list",
            "users": user_list,
            "timestamp": datetime.datetime.now().isoformat()
        }
        self.broadcast_message(message)

    def handle_client(self, client_socket, address):
        """Handle communication with a single client."""
        nickname = None

        try:
            # Nickname setup phase
            while True:
                try:
                    # Request nickname
                    client_socket.send(json.dumps({
                        "type": "nickname_request",
                        "message": "Please enter your nickname:"
                    }).encode('utf-8') + b'\n')

                    # Receive nickname
                    data = client_socket.recv(1024).decode('utf-8').strip()
                    if not data:
                        break

                    try:
                        nickname_data = json.loads(data)
                        proposed_nickname = nickname_data.get(
                            "nickname", "").strip()
                    except:
                        proposed_nickname = data.strip()

                    # Validate nickname
                    if self.validate_nickname(proposed_nickname):
                        nickname = proposed_nickname

                        with self.lock:
                            self.clients[client_socket] = nickname
                            self.nicknames.add(nickname)

                        # Send confirmation
                        client_socket.send(json.dumps({
                            "type": "nickname_accepted",
                            "nickname": nickname
                        }).encode('utf-8') + b'\n')

                        # Log join event
                        self.log_event(
                            f"User joined: {nickname} from {address[0]}:{address[1]}")

                        # Notify other users
                        join_message = {
                            "type": "system",
                            "message": f"{nickname} joined the chat",
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                        self.broadcast_message(join_message, client_socket)

                        # Send user list to all clients
                        self.send_user_list()
                        break
                    else:
                        # Send error
                        client_socket.send(json.dumps({
                            "type": "nickname_error",
                            "message": "Nickname is invalid or already taken. Please choose another."
                        }).encode('utf-8') + b'\n')

                except Exception as e:
                    print(f"Error during nickname setup: {e}")
                    break

            if not nickname:
                return

            # Main chat loop
            while True:
                try:
                    data = client_socket.recv(4096).decode('utf-8').strip()
                    if not data:
                        break

                    # Parse message
                    try:
                        message_data = json.loads(data)
                        self.process_message(
                            message_data, client_socket, nickname)
                    except json.JSONDecodeError:
                        # Handle plain text for backward compatibility
                        message_data = {
                            "type": "text",
                            "content": data,
                            "nickname": nickname
                        }
                        self.process_message(
                            message_data, client_socket, nickname)

                except Exception as e:
                    if self.debug:
                        print(f"DEBUG: Error handling client {nickname}: {e}")
                    else:
                        print(f"Error handling client {nickname}: {e}")
                    break

        except Exception as e:
            print(f"Client {address} error: {e}")
        finally:
            self.disconnect_client(client_socket, nickname)

    def validate_nickname(self, nickname):
        """Validate nickname according to requirements."""
        if not nickname or len(nickname) < 1 or len(nickname) > 20:
            return False

        # Check if nickname is already taken
        if nickname in self.nicknames:
            return False

        # Basic character validation (alphanumeric, spaces, basic punctuation)
        allowed_chars = set(
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-.")
        if not all(c in allowed_chars for c in nickname):
            return False

        return True

    def process_message(self, message_data, sender_socket, nickname):
        """Process different types of messages."""
        message_type = message_data.get("type", "text")
        timestamp = datetime.datetime.now().isoformat()

        if message_type == "text":
            content = message_data.get("content", "")
            if content.strip():
                # Create broadcast message
                broadcast_msg = {
                    "type": "text",
                    "nickname": nickname,
                    "content": content,
                    "timestamp": timestamp
                }

                # Log the message
                self.log_event(f"[CHAT] {nickname}: {content}")

                # Broadcast to other clients
                self.broadcast_message(broadcast_msg, sender_socket)

        elif message_type == "emoji":
            emoji = message_data.get("emoji", "")
            if emoji:
                broadcast_msg = {
                    "type": "emoji",
                    "nickname": nickname,
                    "emoji": emoji,
                    "timestamp": timestamp
                }

                # Log the emoji
                self.log_event(f"[EMOJI] {nickname}: {emoji}")

                # Broadcast to other clients
                self.broadcast_message(broadcast_msg, sender_socket)

        elif message_type == "sticker":
            sticker_id = message_data.get("sticker_id", "")
            if sticker_id:
                broadcast_msg = {
                    "type": "sticker",
                    "nickname": nickname,
                    "sticker_id": sticker_id,
                    "timestamp": timestamp
                }

                # Log the sticker
                self.log_event(f"[STICKER] {nickname}: {sticker_id}")

                # Broadcast to other clients
                self.broadcast_message(broadcast_msg, sender_socket)

        elif message_type == "image":
            image_data = message_data.get("image_data", "")
            image_name = message_data.get("image_name", "image.png")

            if image_data:
                broadcast_msg = {
                    "type": "image",
                    "nickname": nickname,
                    "image_data": image_data,
                    "image_name": image_name,
                    "timestamp": timestamp
                }

                # Log the image
                self.log_event(f"[IMAGE] {nickname}: {image_name}")

                # Broadcast to other clients
                self.broadcast_message(broadcast_msg, sender_socket)

    def disconnect_client(self, client_socket, nickname=None):
        """Disconnect a client and clean up."""
        try:
            if client_socket in self.clients:
                if not nickname:
                    nickname = self.clients[client_socket]

                with self.lock:
                    if client_socket in self.clients:
                        del self.clients[client_socket]
                    if nickname and nickname in self.nicknames:
                        self.nicknames.remove(nickname)

                # Log leave event
                if nickname:
                    self.log_event(f"User left: {nickname}")

                    # Notify other users
                    leave_message = {
                        "type": "system",
                        "message": f"{nickname} left the chat",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                    self.broadcast_message(leave_message)

                    # Send updated user list
                    self.send_user_list()

            client_socket.close()

        except Exception as e:
            print(f"Error disconnecting client: {e}")

    def start(self):
        """Start the chat server."""
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)

            print(f"Chat server started on {self.host}:{self.port}")
            print(f"Logs will be saved to: {self.log_dir}")
            self.log_event(f"Chat server started on {self.host}:{self.port}")

            while True:
                try:
                    client_socket, address = self.socket.accept()
                    print(f"New connection from {address[0]}:{address[1]}")

                    # Start a new thread for each client
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address),
                        daemon=True
                    )
                    client_thread.start()

                except Exception as e:
                    print(f"Error accepting connection: {e}")

        except KeyboardInterrupt:
            print("\nShutting down server...")
            self.log_event("Chat server shutting down")
        except Exception as e:
            print(f"Server error: {e}")
            self.log_event(f"Server error: {e}")
        finally:
            self.socket.close()


def main():
    """Main function to start the server."""
    import sys

    # Default values (similar to Flask app.run defaults)
    host = '0.0.0.0'
    port = 5000
    debug = True

    # Command line arguments
    if len(sys.argv) > 1:
        host = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            port = int(sys.argv[2])
        except ValueError:
            print("Invalid port number. Using default 5000.")
    if len(sys.argv) > 3:
        debug = sys.argv[3].lower() in ('true', '1', 'yes', 'on')

    print("=== Local Network Chat Room Server ===")
    print(f"Starting server on {host}:{port}")
    print(f"Debug mode: {'ON' if debug else 'OFF'}")
    print("Press Ctrl+C to stop the server")
    print()

    server = ChatServer(host, port, debug)
    server.start()


if __name__ == "__main__":
    main()
