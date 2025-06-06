#!/usr/bin/env python3
"""
Local Network Chat Room Server - HTTP/WebSocket Version
Handles multiple client connections via HTTP and WebSocket, message broadcasting, and logging.
"""

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import json
import datetime
import os
from typing import Dict, Set


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for client management
clients: Dict[str, str] = {}  # session_id -> nickname
nicknames: Set[str] = set()  # active nicknames
# room_name -> set of session_ids
rooms: Dict[str, Set[str]] = {'general': set()}

# Logging
log_dir = "chat_logs"


def ensure_log_directory():
    """Create log directory if it doesn't exist."""
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)


def get_log_filename():
    """Generate log filename with current date."""
    today = datetime.datetime.now().strftime("%Y%m%d")
    return os.path.join(log_dir, f"chat_log_{today}.txt")


def log_event(message):
    """Log an event to the daily log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    # Print to console (debug mode)
    print(f"DEBUG: {log_entry.strip()}")

    try:
        with open(get_log_filename(), "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Logging error: {e}")


def validate_nickname(nickname):
    """Validate nickname according to requirements."""
    if not nickname or len(nickname) < 1 or len(nickname) > 20:
        return False

    # Check if nickname is already taken
    if nickname in nicknames:
        return False

    # Basic character validation (alphanumeric, spaces, basic punctuation)
    allowed_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 _-.")
    if not all(c in allowed_chars for c in nickname):
        return False

    return True


@app.route('/')
def index():
    """Serve the chat interface."""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>Chat Room</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        #messages { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin: 10px 0; }
        #messageInput { width: 70%; padding: 10px; }
        #sendButton { padding: 10px 20px; }
        .message { margin: 5px 0; }
        .system { color: #666; font-style: italic; }
        .user { color: #333; }
        .timestamp { color: #999; font-size: 0.8em; }
        #userList { border: 1px solid #ccc; height: 200px; overflow-y: scroll; padding: 10px; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Chat Room</h1>
    
    <div id="nicknameSection">
        <input type="text" id="nicknameInput" placeholder="Enter your nickname..." maxlength="20">
        <button onclick="setNickname()">Join Chat</button>
    </div>
    
    <div id="chatSection" style="display: none;">
        <div id="messages"></div>
        <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
        <button id="sendButton" onclick="sendMessage()">Send</button>
        
        <h3>Online Users:</h3>
        <div id="userList"></div>
    </div>

    <script>
        const socket = io();
        let nickname = '';
        
        function setNickname() {
            const nicknameInput = document.getElementById('nicknameInput');
            const proposedNickname = nicknameInput.value.trim();
            
            if (proposedNickname) {
                socket.emit('set_nickname', {nickname: proposedNickname});
            }
        }
        
        function sendMessage() {
            const messageInput = document.getElementById('messageInput');
            const message = messageInput.value.trim();
            
            if (message) {
                socket.emit('send_message', {
                    type: 'text',
                    content: message
                });
                messageInput.value = '';
            }
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                if (document.getElementById('nicknameSection').style.display !== 'none') {
                    setNickname();
                } else {
                    sendMessage();
                }
            }
        }
        
        function addMessage(data) {
            const messages = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            
            const timestamp = new Date(data.timestamp).toLocaleTimeString();
            
            if (data.type === 'system') {
                messageDiv.className += ' system';
                messageDiv.innerHTML = `<span class="timestamp">[${timestamp}]</span> ${data.message}`;
            } else {
                messageDiv.className += ' user';
                messageDiv.innerHTML = `<span class="timestamp">[${timestamp}]</span> <strong>${data.nickname}:</strong> ${data.content}`;
            }
            
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }
        
        function updateUserList(users) {
            const userList = document.getElementById('userList');
            userList.innerHTML = '';
            
            users.forEach(user => {
                const userDiv = document.createElement('div');
                userDiv.textContent = user;
                userList.appendChild(userDiv);
            });
        }
        
        // Socket event handlers
        socket.on('nickname_accepted', function(data) {
            nickname = data.nickname;
            document.getElementById('nicknameSection').style.display = 'none';
            document.getElementById('chatSection').style.display = 'block';
            document.getElementById('messageInput').focus();
        });
        
        socket.on('nickname_error', function(data) {
            alert(data.message);
        });
        
        socket.on('message', function(data) {
            addMessage(data);
        });
        
        socket.on('user_list', function(data) {
            updateUserList(data.users);
        });
        
        // Focus nickname input on load
        document.getElementById('nicknameInput').focus();
    </script>
</body>
</html>
    '''


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"Client connected: {request.sid}")
    log_event(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    session_id = request.sid

    if session_id in clients:
        nickname = clients[session_id]

        # Remove from clients and nicknames
        del clients[session_id]
        nicknames.discard(nickname)

        # Log leave event
        log_event(f"User left: {nickname}")

        # Notify other users
        socketio.emit('message', {
            "type": "system",
            "message": f"{nickname} left the chat",
            "timestamp": datetime.datetime.now().isoformat()
        })

        # Send updated user list
        socketio.emit('user_list', {"users": list(nicknames)})

    print(f"Client disconnected: {session_id}")


@socketio.on('set_nickname')
def handle_set_nickname(data):
    """Handle nickname setting."""
    session_id = request.sid
    proposed_nickname = data.get('nickname', '').strip()

    if validate_nickname(proposed_nickname):
        # Set nickname
        clients[session_id] = proposed_nickname
        nicknames.add(proposed_nickname)

        # Send confirmation
        emit('nickname_accepted', {'nickname': proposed_nickname})

        # Log join event
        log_event(f"User joined: {proposed_nickname}")

        # Notify other users
        socketio.emit('message', {
            "type": "system",
            "message": f"{proposed_nickname} joined the chat",
            "timestamp": datetime.datetime.now().isoformat()
        }, room=None, include_self=False)

        # Send user list to all clients
        socketio.emit('user_list', {"users": list(nicknames)})

    else:
        emit('nickname_error', {
            'message': 'Nickname is invalid or already taken. Please choose another.'
        })


@socketio.on('send_message')
def handle_send_message(data):
    """Handle incoming messages."""
    session_id = request.sid

    if session_id not in clients:
        return

    nickname = clients[session_id]
    message_type = data.get('type', 'text')
    timestamp = datetime.datetime.now().isoformat()

    if message_type == 'text':
        content = data.get('content', '').strip()
        if content:
            # Create broadcast message
            broadcast_msg = {
                "type": "text",
                "nickname": nickname,
                "content": content,
                "timestamp": timestamp
            }

            # Log the message
            log_event(f"[CHAT] {nickname}: {content}")

            # Broadcast to all clients
            socketio.emit('message', broadcast_msg)


def main():
    """Main function to start the server."""
    import sys

    # Default values
    host = '0.0.0.0'
    port = 5000
    debug = True

    # Command line arguments
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print("Invalid port number. Using default 5000.")

    # Ensure log directory exists
    ensure_log_directory()

    print("=== Local Network Chat Room Server (HTTP/WebSocket) ===")
    print(f"Server starting on {host}:{port}")
    print(f"Debug mode: {'ON' if debug else 'OFF'}")
    print(f"Access the chat at: http://103.149.252.221:{port}/")
    print(f"Local access: http://localhost:{port}/")
    print("Press Ctrl+C to stop the server")
    print()

    log_event(f"Chat server started on {host}:{port}")

    # Start the server
    socketio.run(app, host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
