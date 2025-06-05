#!/usr/bin/env python3
"""
Local Network Chat Room Server - HTTP/WebSocket Version
Handles multiple client connections via HTTP and WebSocket, message broadcasting, and logging.
"""

from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
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
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #333; }
        #messages { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin: 10px 0; background: #fafafa; border-radius: 5px; }
        #messageInput { width: 70%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        #sendButton { padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
        #sendButton:hover { background: #0056b3; }
        .message { margin: 5px 0; padding: 5px; border-radius: 3px; }
        .system { color: #666; font-style: italic; background: #e9ecef; }
        .user { color: #333; background: #fff; border-left: 3px solid #007bff; padding-left: 10px; }
        .timestamp { color: #999; font-size: 0.8em; }
        #userList { border: 1px solid #ccc; height: 150px; overflow-y: scroll; padding: 10px; margin: 10px 0; background: #fafafa; border-radius: 5px; }
        #nicknameInput { width: 70%; padding: 10px; border: 1px solid #ccc; border-radius: 5px; }
        .join-button { padding: 10px 20px; background: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .join-button:hover { background: #1e7e34; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Chat Room</h1>
        
        <div id="nicknameSection">
            <p>Chào mừng! Vui lòng nhập nickname để tham gia chat:</p>
            <input type="text" id="nicknameInput" placeholder="Nhập nickname của bạn..." maxlength="20">
            <button class="join-button" onclick="setNickname()">Tham gia Chat</button>
        </div>
        
        <div id="chatSection" style="display: none;">
            <div id="messages"></div>
            <div style="margin: 10px 0;">
                <input type="text" id="messageInput" placeholder="Nhập tin nhắn..." onkeypress="handleKeyPress(event)">
                <button id="sendButton" onclick="sendMessage()">Gửi</button>
            </div>
            
            <h3>👥 Người dùng online:</h3>
            <div id="userList"></div>
        </div>
    </div>

    <script>
        const socket = io();
        let nickname = '';
        
        function setNickname() {
            const nicknameInput = document.getElementById('nicknameInput');
            const proposedNickname = nicknameInput.value.trim();
            
            if (proposedNickname) {
                socket.emit('set_nickname', {nickname: proposedNickname});
            } else {
                alert('Vui lòng nhập nickname!');
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
            
            if (users.length === 0) {
                userList.innerHTML = '<em>Chưa có ai online</em>';
                return;
            }
            
            users.forEach(user => {
                const userDiv = document.createElement('div');
                userDiv.textContent = '🟢 ' + user;
                userDiv.style.padding = '2px 0';
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
            document.getElementById('nicknameInput').focus();
        });
        
        socket.on('message', function(data) {
            addMessage(data);
        });
        
        socket.on('user_list', function(data) {
            updateUserList(data.users);
        });
        
        socket.on('connect', function() {
            console.log('Đã kết nối tới server');
        });
        
        socket.on('disconnect', function() {
            console.log('Mất kết nối tới server');
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
            "message": f"{nickname} đã rời khỏi phòng chat",
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
            "message": f"{proposed_nickname} đã tham gia phòng chat",
            "timestamp": datetime.datetime.now().isoformat()
        }, include_self=False)

        # Send user list to all clients
        socketio.emit('user_list', {"users": list(nicknames)})

    else:
        emit('nickname_error', {
            'message': 'Nickname không hợp lệ hoặc đã được sử dụng. Vui lòng chọn nickname khác.'
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
            print("Port không hợp lệ. Sử dụng port mặc định 5000.")

    # Ensure log directory exists
    ensure_log_directory()

    print("="*60)
    print("🔥 LOCAL NETWORK CHAT ROOM SERVER (HTTP/WebSocket)")
    print("="*60)
    print(f"📡 Server đang khởi động trên {host}:{port}")
    print(f"🐛 Debug mode: {'BẬT' if debug else 'TẮT'}")
    print(f"🌐 Truy cập chat tại: http://103.149.252.221:{port}/")
    print(f"🏠 Truy cập local: http://localhost:{port}/")
    print("⚡ Sử dụng Ctrl+C để dừng server")
    print("="*60)
    print()

    log_event(f"Chat server started on {host}:{port}")

    try:
        # Start the server
        socketio.run(app, host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n🔴 Đang tắt server...")
        log_event("Chat server shutting down")
    except Exception as e:
        print(f"❌ Lỗi server: {e}")
        log_event(f"Server error: {e}")


if __name__ == "__main__":
    main()
