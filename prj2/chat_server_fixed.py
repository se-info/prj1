#!/usr/bin/env python3
"""
Advanced Local Network Chat Room Server - HTTP/WebSocket Version (Fixed SSL)
Enhanced with modern UI, emoji, image sharing, Vietnamese names, notifications, and read receipts.
No eventlet dependency to avoid SSL issues.
"""

from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO, emit
import json
import datetime
import os
import base64
import uuid
from typing import Dict, Set, List
import re
import threading


app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Use threading instead of eventlet to avoid SSL issues
socketio = SocketIO(app,
                    cors_allowed_origins="*",
                    max_http_buffer_size=16*1024*1024,
                    async_mode='threading',  # Fixed: use threading instead of eventlet
                    logger=True,
                    engineio_logger=True)

# Global variables for client management
clients: Dict[str, Dict] = {}  # session_id -> {nickname, join_time, last_seen}
nicknames: Set[str] = set()  # active nicknames
messages: List[Dict] = []  # Store messages in memory for read receipts
# message_id -> set of user_ids who read
message_reads: Dict[str, Set[str]] = {}

# Directories
log_dir = "chat_logs"
upload_dir = "uploads"

# Thread lock for thread safety
clients_lock = threading.Lock()


def ensure_directories():
    """Create necessary directories if they don't exist."""
    for directory in [log_dir, upload_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)


def get_log_filename():
    """Generate log filename with current date."""
    today = datetime.datetime.now().strftime("%Y%m%d")
    return os.path.join(log_dir, f"chat_log_{today}.txt")


def log_event(message):
    """Log an event to the daily log file."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}\n"

    print(f"DEBUG: {log_entry.strip()}")

    try:
        with open(get_log_filename(), "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Logging error: {e}")


def validate_nickname(nickname):
    """Validate nickname with Vietnamese character support."""
    if not nickname or len(nickname) < 1 or len(nickname) > 20:
        return False

    # Check if nickname is already taken
    with clients_lock:
        if nickname in nicknames:
            return False

    # Allow Vietnamese characters, alphanumeric, spaces, basic punctuation
    # Vietnamese regex pattern
    vietnamese_pattern = r'^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂẠẢẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăạảấầẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪếệỉịọỏốồổỗộớờởỡợụủứừỬỮỰỲỴÝỶỸửữựỳỵýỷỹ0-9 _.-]+$'

    if not re.match(vietnamese_pattern, nickname):
        return False

    return True


@app.route('/')
def index():
    """Serve the enhanced chat interface."""
    return '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 Advanced Chat Room (Fixed)</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        :root {
            /* Default Theme (Red) */
            --bg-gradient: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            --container-bg: rgba(255,255,255,0.95);
            --header-gradient: linear-gradient(90deg, #ff4757, #ff3838);
            --text-color: #333;
            --sidebar-bg: #f8f9fa;
            --sidebar-border: #dee2e6;
            --message-bg: linear-gradient(to bottom, #fafafa, #ffffff);
            --own-message-bg: linear-gradient(135deg, #ff4757, #ff3838);
            --other-message-bg: #e9ecef;
            --system-message-bg: linear-gradient(90deg, #ff6b6b, #ff4757);
            --input-bg: white;
            --input-border: #dee2e6;
            --input-focus: #ff4757;
            --user-item-bg: white;
            --emoji-picker-bg: white;
            --join-card-bg: white;
            --shadow-color: rgba(0,0,0,0.1);
        }
        
        [data-theme="dark"] {
            --bg-gradient: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            --container-bg: rgba(44, 62, 80, 0.95);
            --header-gradient: linear-gradient(90deg, #34495e, #2c3e50);
            --text-color: #ecf0f1;
            --sidebar-bg: #2c3e50;
            --sidebar-border: #34495e;
            --message-bg: linear-gradient(to bottom, #34495e, #2c3e50);
            --own-message-bg: linear-gradient(135deg, #3498db, #2980b9);
            --other-message-bg: #34495e;
            --system-message-bg: linear-gradient(90deg, #9b59b6, #8e44ad);
            --input-bg: #34495e;
            --input-border: #2c3e50;
            --input-focus: #3498db;
            --user-item-bg: #34495e;
            --emoji-picker-bg: #2c3e50;
            --join-card-bg: #34495e;
            --shadow-color: rgba(0,0,0,0.3);
        }
        
        [data-theme="white"] {
            --bg-gradient: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            --container-bg: rgba(255,255,255,0.98);
            --header-gradient: linear-gradient(90deg, #6c757d, #495057);
            --text-color: #212529;
            --sidebar-bg: #ffffff;
            --sidebar-border: #dee2e6;
            --message-bg: linear-gradient(to bottom, #ffffff, #f8f9fa);
            --own-message-bg: linear-gradient(135deg, #007bff, #0056b3);
            --other-message-bg: #f8f9fa;
            --system-message-bg: linear-gradient(90deg, #6c757d, #495057);
            --input-bg: white;
            --input-border: #ced4da;
            --input-focus: #007bff;
            --user-item-bg: white;
            --emoji-picker-bg: white;
            --join-card-bg: white;
            --shadow-color: rgba(0,0,0,0.08);
        }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: var(--bg-gradient);
            min-height: 100vh;
            color: var(--text-color);
            transition: all 0.3s ease;
        }
        
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: var(--container-bg);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px var(--shadow-color);
            transition: all 0.3s ease;
        }
        
        .header {
            background: var(--header-gradient);
            color: white;
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px var(--shadow-color);
            position: relative;
        }
        
        .header h1 {
            font-size: 2em;
            margin-bottom: 5px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .theme-selector {
            position: absolute;
            top: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .theme-button {
            width: 30px;
            height: 30px;
            border-radius: 50%;
            border: 2px solid white;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .theme-button:hover {
            transform: scale(1.1);
            box-shadow: 0 4px 10px rgba(0,0,0,0.3);
        }
        
        .theme-button.active {
            border-width: 3px;
            box-shadow: 0 0 10px rgba(255,255,255,0.8);
        }
        
        .theme-red { background: linear-gradient(135deg, #ff4757, #ff3838); }
        .theme-dark { background: linear-gradient(135deg, #2c3e50, #34495e); }
        .theme-white { background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-color: #333; }
        .theme-custom { background: conic-gradient(from 0deg, #ff6b6b, #4ecdc4, #45b7d1, #f9ca24, #f0932b, #eb4d4b, #6c5ce7); }
        
        .theme-label {
            color: white;
            font-size: 0.9em;
            margin-right: 10px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        .custom-theme-panel {
            position: absolute;
            top: 100%;
            right: 0;
            background: var(--join-card-bg);
            border: 1px solid var(--sidebar-border);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 8px 25px var(--shadow-color);
            display: none;
            z-index: 1000;
            min-width: 250px;
            color: var(--text-color);
        }
        
        .color-input-group {
            margin-bottom: 15px;
        }
        
        .color-input-group label {
            display: block;
            margin-bottom: 5px;
            font-size: 0.9em;
        }
        
        .color-input-group input[type="color"] {
            width: 100%;
            height: 40px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        
        .status-badge {
            background: #28a745;
            color: white;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            margin-left: 10px;
        }
        
        .chat-container {
            display: flex;
            flex: 1;
            overflow: hidden;
        }
        
        .sidebar {
            width: 300px;
            background: var(--sidebar-bg);
            border-right: 1px solid var(--sidebar-border);
            display: flex;
            flex-direction: column;
            transition: all 0.3s ease;
        }
        
        .main-chat {
            flex: 1;
            display: flex;
            flex-direction: column;
        }
        
        #messages { 
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: var(--message-bg);
            transition: all 0.3s ease;
        }
        
        .message { 
            margin: 10px 0; 
            padding: 12px 16px;
            border-radius: 18px;
            max-width: 70%;
            word-wrap: break-word;
            position: relative;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.own {
            background: var(--own-message-bg);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }
        
        .message.other {
            background: var(--other-message-bg);
            color: var(--text-color);
            margin-right: auto;
            border-bottom-left-radius: 4px;
        }
        
        .message.system { 
            background: var(--system-message-bg);
            color: white;
            text-align: center;
            margin: 5px auto;
            max-width: 80%;
            border-radius: 20px;
            font-style: italic;
        }
        
        .message-header {
            font-size: 0.8em;
            opacity: 0.8;
            margin-bottom: 4px;
        }
        
        .message-content {
            font-size: 1em;
            line-height: 1.4;
        }
        
        .message-image {
            max-width: 200px;
            max-height: 200px;
            border-radius: 8px;
            margin-top: 5px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .message-image:hover {
            transform: scale(1.05);
        }
        
        .message-time {
            font-size: 0.7em;
            opacity: 0.6;
            margin-top: 4px;
        }
        
        .read-status {
            font-size: 0.7em;
            opacity: 0.6;
            margin-top: 2px;
            color: #28a745;
        }
        
        .input-area {
            padding: 20px;
            background: var(--input-bg);
            border-top: 1px solid var(--sidebar-border);
            box-shadow: 0 -2px 10px var(--shadow-color);
            transition: all 0.3s ease;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
            align-items: end;
        }
        
        #messageInput { 
            flex: 1;
            padding: 12px 16px;
            border: 2px solid var(--input-border);
            border-radius: 25px;
            font-size: 14px;
            resize: none;
            max-height: 100px;
            min-height: 44px;
            transition: all 0.3s;
            background: var(--input-bg);
            color: var(--text-color);
        }
        
        #messageInput:focus {
            border-color: var(--input-focus);
            outline: none;
        }
        
        .input-buttons {
            display: flex;
            gap: 5px;
        }
        
        .btn {
            padding: 12px;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 16px;
            width: 44px;
            height: 44px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .btn-primary { background: #007bff; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-warning { background: #ffc107; color: #333; }
        .btn-info { background: #17a2b8; color: white; }
        
        .btn:hover { transform: scale(1.1); box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
        
        .emoji-picker {
            position: absolute;
            bottom: 60px;
            right: 20px;
            background: var(--emoji-picker-bg);
            border: 1px solid var(--sidebar-border);
            border-radius: 10px;
            padding: 15px;
            box-shadow: 0 8px 25px var(--shadow-color);
            display: none;
            max-width: 300px;
            z-index: 1000;
            color: var(--text-color);
            transition: all 0.3s ease;
        }
        
        .emoji-grid {
            display: grid;
            grid-template-columns: repeat(8, 1fr);
            gap: 5px;
            max-height: 200px;
            overflow-y: auto;
        }
        
        .emoji {
            font-size: 20px;
            padding: 5px;
            cursor: pointer;
            border-radius: 5px;
            text-align: center;
            transition: background 0.2s;
        }
        
        .emoji:hover {
            background: #f8f9fa;
        }
        
        .user-list {
            padding: 20px;
            flex: 1;
        }
        
        .user-list h3 {
            color: #495057;
            margin-bottom: 15px;
            font-size: 1.1em;
        }
        
        .user-item {
            display: flex;
            align-items: center;
            padding: 8px 12px;
            margin: 5px 0;
            background: var(--user-item-bg);
            border-radius: 10px;
            box-shadow: 0 2px 5px var(--shadow-color);
            transition: all 0.3s ease;
            color: var(--text-color);
        }
        
        .user-item:hover {
            transform: translateX(5px);
        }
        
        .user-status {
            width: 8px;
            height: 8px;
            background: #28a745;
            border-radius: 50%;
            margin-right: 10px;
        }
        
        .join-section {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            padding: 40px;
            text-align: center;
        }
        
        .join-card {
            background: var(--join-card-bg);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 10px 30px var(--shadow-color);
            max-width: 400px;
            width: 100%;
            transition: all 0.3s ease;
            color: var(--text-color);
        }
        
        .join-card h2 {
            color: #333;
            margin-bottom: 20px;
            font-size: 1.8em;
        }
        
        .join-card p {
            color: #666;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        
        #nicknameInput { 
            width: 100%;
            padding: 15px;
            border: 2px solid var(--input-border);
            border-radius: 10px;
            font-size: 16px;
            margin-bottom: 20px;
            transition: all 0.3s;
            background: var(--input-bg);
            color: var(--text-color);
        }
        
        #nicknameInput:focus {
            border-color: var(--input-focus);
            outline: none;
        }
        
        .join-button { 
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
        }
        
        .join-button:hover { 
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(40,167,69,0.3);
        }
        
        .file-input {
            display: none;
        }
        
        .typing-indicator {
            padding: 10px 20px;
            color: #666;
            font-style: italic;
            font-size: 0.9em;
        }
        
        .notification-permission {
            background: #fff3cd;
            color: #856404;
            padding: 10px;
            text-align: center;
            border-bottom: 1px solid #ffeaa7;
        }
        
        .notification-permission button {
            background: #ffc107;
            color: #333;
            border: none;
            padding: 5px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin-left: 10px;
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .chat-container { flex-direction: column; }
            .sidebar { width: 100%; max-height: 200px; }
            .message { max-width: 90%; }
            .input-container { flex-wrap: wrap; }
            
            .theme-selector {
                position: relative;
                top: auto;
                right: auto;
                margin-bottom: 10px;
                justify-content: center;
            }
            
            .theme-label {
                font-size: 0.8em;
            }
            
            .theme-button {
                width: 25px;
                height: 25px;
            }
            
            .custom-theme-panel {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 90%;
                max-width: 300px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="theme-selector">
                <span class="theme-label">🎨</span>
                <div class="theme-button theme-red active" data-theme="default" title="Chủ đề đỏ (mặc định)"></div>
                <div class="theme-button theme-dark" data-theme="dark" title="Chế độ tối"></div>
                <div class="theme-button theme-white" data-theme="white" title="Chế độ sáng"></div>
                <div class="theme-button theme-custom" data-theme="custom" title="Tùy chỉnh màu sắc"></div>
                <div class="custom-theme-panel" id="customThemePanel">
                    <h4 style="margin-bottom: 15px;">🎨 Tùy chỉnh màu sắc</h4>
                    <div class="color-input-group">
                        <label>Màu nền chính:</label>
                        <input type="color" id="bgColor1" value="#ff6b6b">
                    </div>
                    <div class="color-input-group">
                        <label>Màu nền phụ:</label>
                        <input type="color" id="bgColor2" value="#ee5a52">
                    </div>
                    <div class="color-input-group">
                        <label>Màu tin nhắn của bạn:</label>
                        <input type="color" id="ownMessageColor" value="#ff4757">
                    </div>
                    <div class="color-input-group">
                        <label>Màu header:</label>
                        <input type="color" id="headerColor" value="#ff4757">
                    </div>
                    <button onclick="applyCustomTheme()" style="width: 100%; padding: 10px; background: var(--input-focus); color: white; border: none; border-radius: 5px; cursor: pointer;">Áp dụng</button>
                </div>
            </div>
            <h1>🔥 Private Room <span class="status-badge">SSL Fixed</span></h1>
            <p>Kết nối, chia sẻ và trò chuyện cùng bạn bè - Không có lỗi SSL!</p>
        </div>
        
        <div id="notificationPermission" class="notification-permission" style="display: none;">
            Cho phép thông báo để nhận tin nhắn mới?
            <button onclick="requestNotificationPermission()">Cho phép</button>
            <button onclick="hideNotificationBanner()">Bỏ qua</button>
        </div>
        
        <div id="joinSection" class="join-section">
            <div class="join-card">
                <h2>🎉 Chào mừng bạn!</h2>
                <p>Vui lòng nhập nickname để tham gia chat room. Bạn có thể sử dụng tiếng Việt có dấu!</p>
                <input type="text" id="nicknameInput" placeholder="Nhập nickname của bạn... (VD: Nguyễn Văn A)" maxlength="20">
                <button class="join-button" onclick="setNickname()">
                    <i class="fas fa-sign-in-alt"></i> Tham gia Chat
                </button>
            </div>
        </div>
        
        <div id="chatSection" class="chat-container" style="display: none;">
            <div class="sidebar">
                <div class="user-list">
                    <h3><i class="fas fa-users"></i> Người dùng online (<span id="userCount">0</span>)</h3>
                    <div id="userList"></div>
                </div>
            </div>
            
            <div class="main-chat">
                <div id="messages"></div>
                <div id="typingIndicator" class="typing-indicator" style="display: none;"></div>
                
                <div class="input-area">
                    <div class="input-container">
                        <textarea id="messageInput" placeholder="Nhập tin nhắn..." rows="1"></textarea>
                        <div class="input-buttons">
                            <button class="btn btn-warning" onclick="toggleEmojiPicker()" title="Emoji">
                                <i class="fas fa-smile"></i>
                            </button>
                            <button class="btn btn-info" onclick="document.getElementById('fileInput').click()" title="Gửi ảnh">
                                <i class="fas fa-image"></i>
                            </button>
                            <button class="btn btn-primary" onclick="sendMessage()" title="Gửi">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="emoji-picker" id="emojiPicker">
            <h4 style="margin-bottom: 10px;">😊 Chọn emoji</h4>
            <div class="emoji-grid" id="emojiGrid"></div>
        </div>
        
        <input type="file" id="fileInput" class="file-input" accept="image/*" onchange="handleFileSelect(event)">
    </div>

    <script>
        const socket = io();
        let nickname = '';
        let currentUsers = [];
        let typingTimeout = null;
        let isTyping = false;
        let currentTheme = 'default';
        
        // Theme management
        function initThemeSystem() {
            // Load saved theme from localStorage
            const savedTheme = localStorage.getItem('chatTheme') || 'default';
            switchTheme(savedTheme);
            
            // Add click handlers for theme buttons
            document.querySelectorAll('.theme-button').forEach(button => {
                button.addEventListener('click', function() {
                    const theme = this.getAttribute('data-theme');
                    if (theme === 'custom') {
                        toggleCustomThemePanel();
                    } else {
                        switchTheme(theme);
                    }
                });
            });
            
            // Close custom panel when clicking outside
            document.addEventListener('click', function(e) {
                const panel = document.getElementById('customThemePanel');
                const customButton = document.querySelector('[data-theme="custom"]');
                if (!panel.contains(e.target) && !customButton.contains(e.target)) {
                    panel.style.display = 'none';
                }
            });
        }
        
        function switchTheme(theme) {
            const body = document.body;
            const themeButtons = document.querySelectorAll('.theme-button');
            
            // Remove active class from all buttons
            themeButtons.forEach(btn => btn.classList.remove('active'));
            
            // Set theme attribute
            if (theme === 'default') {
                body.removeAttribute('data-theme');
                document.querySelector('[data-theme="default"]').classList.add('active');
            } else {
                body.setAttribute('data-theme', theme);
                document.querySelector(`[data-theme="${theme}"]`).classList.add('active');
            }
            
            currentTheme = theme;
            localStorage.setItem('chatTheme', theme);
            
            // Hide custom panel
            document.getElementById('customThemePanel').style.display = 'none';
        }
        
        function toggleCustomThemePanel() {
            const panel = document.getElementById('customThemePanel');
            const isVisible = panel.style.display === 'block';
            panel.style.display = isVisible ? 'none' : 'block';
            
            if (!isVisible) {
                // Load current custom colors if any
                loadCustomColors();
            }
        }
        
        function loadCustomColors() {
            const customTheme = localStorage.getItem('customTheme');
            if (customTheme) {
                const colors = JSON.parse(customTheme);
                document.getElementById('bgColor1').value = colors.bgColor1 || '#ff6b6b';
                document.getElementById('bgColor2').value = colors.bgColor2 || '#ee5a52';
                document.getElementById('ownMessageColor').value = colors.ownMessageColor || '#ff4757';
                document.getElementById('headerColor').value = colors.headerColor || '#ff4757';
            }
        }
        
        function applyCustomTheme() {
            const bgColor1 = document.getElementById('bgColor1').value;
            const bgColor2 = document.getElementById('bgColor2').value;
            const ownMessageColor = document.getElementById('ownMessageColor').value;
            const headerColor = document.getElementById('headerColor').value;
            
            // Save custom colors
            const customColors = { bgColor1, bgColor2, ownMessageColor, headerColor };
            localStorage.setItem('customTheme', JSON.stringify(customColors));
            
            // Apply custom theme
            const root = document.documentElement;
            root.style.setProperty('--bg-gradient', `linear-gradient(135deg, ${bgColor1} 0%, ${bgColor2} 100%)`);
            root.style.setProperty('--header-gradient', `linear-gradient(90deg, ${headerColor}, ${headerColor}dd)`);
            root.style.setProperty('--own-message-bg', `linear-gradient(135deg, ${ownMessageColor}, ${ownMessageColor}dd)`);
            root.style.setProperty('--system-message-bg', `linear-gradient(90deg, ${ownMessageColor}, ${headerColor})`);
            root.style.setProperty('--input-focus', ownMessageColor);
            
            // Update active theme
            document.querySelectorAll('.theme-button').forEach(btn => btn.classList.remove('active'));
            document.querySelector('[data-theme="custom"]').classList.add('active');
            
            currentTheme = 'custom';
            localStorage.setItem('chatTheme', 'custom');
            
            // Hide panel
            document.getElementById('customThemePanel').style.display = 'none';
            
            showNotification('🎨 Chủ đề tùy chỉnh', 'Đã áp dụng màu sắc mới!');
        }
        
        // Load custom theme if it was previously applied
        function loadSavedCustomTheme() {
            if (currentTheme === 'custom') {
                const customTheme = localStorage.getItem('customTheme');
                if (customTheme) {
                    const colors = JSON.parse(customTheme);
                    const root = document.documentElement;
                    root.style.setProperty('--bg-gradient', `linear-gradient(135deg, ${colors.bgColor1} 0%, ${colors.bgColor2} 100%)`);
                    root.style.setProperty('--header-gradient', `linear-gradient(90deg, ${colors.headerColor}, ${colors.headerColor}dd)`);
                    root.style.setProperty('--own-message-bg', `linear-gradient(135deg, ${colors.ownMessageColor}, ${colors.ownMessageColor}dd)`);
                    root.style.setProperty('--system-message-bg', `linear-gradient(90deg, ${colors.ownMessageColor}, ${colors.headerColor})`);
                    root.style.setProperty('--input-focus', colors.ownMessageColor);
                }
            }
        }

        // Emoji list
        const emojis = [
            '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍', '🥰',
            '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '🤪', '🤨', '🧐', '🤓', '😎', '🤩', '🥳', '😏',
            '😒', '😞', '😔', '😟', '😕', '🙁', '☹️', '😣', '😖', '😫', '😩', '🥺', '😢', '😭', '😤', '😠',
            '👍', '👎', '👌', '🤝', '👏', '🙌', '👐', '🤲', '🤞', '✌️', '🤟', '🤘', '🤙', '💪', '🦾', '🖕',
            '❤️', '🧡', '💛', '💚', '💙', '💜', '🖤', '🤍', '🤎', '💔', '❣️', '💕', '💞', '💓', '💗', '💖',
            '🎉', '🎊', '🎈', '🎁', '🏆', '🥇', '🥈', '🥉', '⭐', '🌟', '💫', '✨', '🔥', '💯', '✅', '❌'
        ];
        
        // Initialize emoji picker
        function initEmojiPicker() {
            const emojiGrid = document.getElementById('emojiGrid');
            emojis.forEach(emoji => {
                const emojiElement = document.createElement('div');
                emojiElement.className = 'emoji';
                emojiElement.textContent = emoji;
                emojiElement.onclick = () => insertEmoji(emoji);
                emojiGrid.appendChild(emojiElement);
            });
        }
        
        function toggleEmojiPicker() {
            const picker = document.getElementById('emojiPicker');
            picker.style.display = picker.style.display === 'none' ? 'block' : 'none';
        }
        
        function insertEmoji(emoji) {
            const messageInput = document.getElementById('messageInput');
            const start = messageInput.selectionStart;
            const end = messageInput.selectionEnd;
            const text = messageInput.value;
            messageInput.value = text.substring(0, start) + emoji + text.substring(end);
            messageInput.focus();
            messageInput.selectionStart = messageInput.selectionEnd = start + emoji.length;
            toggleEmojiPicker();
        }
        
        // Notification functions
        function requestNotificationPermission() {
            if ("Notification" in window) {
                Notification.requestPermission().then(function (permission) {
                    if (permission === "granted") {
                        hideNotificationBanner();
                    }
                });
            }
            hideNotificationBanner();
        }
        
        function hideNotificationBanner() {
            document.getElementById('notificationPermission').style.display = 'none';
        }
        
        function showNotification(title, body) {
            if ("Notification" in window && Notification.permission === "granted") {
                new Notification(title, {
                    body: body,
                    icon: '🔥'
                });
            }
        }
        
        // Auto-resize textarea
        function autoResize() {
            const textarea = document.getElementById('messageInput');
            textarea.style.height = 'auto';
            textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
        }
        
        document.getElementById('messageInput').addEventListener('input', function() {
            autoResize();
            handleTyping();
        });
        
        // Typing indicator
        function handleTyping() {
            if (!isTyping) {
                isTyping = true;
                socket.emit('typing_start');
            }
            
            clearTimeout(typingTimeout);
            typingTimeout = setTimeout(() => {
                isTyping = false;
                socket.emit('typing_stop');
            }, 1000);
        }
        
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
                autoResize();
                toggleEmojiPicker();
            }
        }
        
        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file && file.type.startsWith('image/')) {
                if (file.size > 5 * 1024 * 1024) { // 5MB limit
                    alert('Ảnh quá lớn! Vui lòng chọn ảnh nhỏ hơn 5MB.');
                    return;
                }
                
                const reader = new FileReader();
                reader.onload = function(e) {
                    const imageData = e.target.result;
                    socket.emit('send_message', {
                        type: 'image',
                        content: imageData,
                        fileName: file.name
                    });
                };
                reader.readAsDataURL(file);
            }
            event.target.value = '';
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                if (document.getElementById('joinSection').style.display !== 'none') {
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
            messageDiv.setAttribute('data-message-id', data.id || '');
            
            const timestamp = new Date(data.timestamp).toLocaleTimeString('vi-VN');
            
            if (data.type === 'system') {
                messageDiv.className += ' system';
                messageDiv.innerHTML = `
                    <div class="message-content">${data.message}</div>
                    <div class="message-time">${timestamp}</div>
                `;
            } else {
                const isOwn = data.nickname === nickname;
                messageDiv.className += isOwn ? ' own' : ' other';
                
                let content = '';
                if (data.type === 'image') {
                    content = `<img src="${data.content}" alt="Shared image" class="message-image" onclick="openImageModal(this.src)">`;
                } else {
                    content = data.content;
                }
                
                messageDiv.innerHTML = `
                    <div class="message-header">${data.nickname}</div>
                    <div class="message-content">${content}</div>
                    <div class="message-time">${timestamp}</div>
                    ${isOwn && data.reads !== undefined ? `<div class="read-status">${data.reads} người đã xem</div>` : ''}
                `;
            }
            
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
            
            // Mark message as read
            if (data.id && data.nickname !== nickname) {
                socket.emit('mark_read', {message_id: data.id});
                
                // Show notification for new messages
                if (document.hidden) {
                    showNotification(`${data.nickname}`, 
                        data.type === 'image' ? 'Đã gửi một ảnh' : data.content);
                }
            }
        }
        
        function openImageModal(src) {
            const modal = document.createElement('div');
            modal.style.cssText = `
                position: fixed; top: 0; left: 0; width: 100%; height: 100%; 
                background: rgba(0,0,0,0.8); display: flex; align-items: center; 
                justify-content: center; z-index: 10000; cursor: pointer;
            `;
            
            const img = document.createElement('img');
            img.src = src;
            img.style.cssText = 'max-width: 90%; max-height: 90%; border-radius: 10px;';
            
            modal.appendChild(img);
            modal.onclick = () => document.body.removeChild(modal);
            document.body.appendChild(modal);
        }
        
        function updateUserList(users) {
            const userList = document.getElementById('userList');
            const userCount = document.getElementById('userCount');
            userList.innerHTML = '';
            userCount.textContent = users.length;
            
            currentUsers = users;
            
            if (users.length === 0) {
                userList.innerHTML = '<div style="text-align: center; color: #666; padding: 20px;">Chưa có ai online</div>';
                return;
            }
            
            users.forEach(user => {
                const userDiv = document.createElement('div');
                userDiv.className = 'user-item';
                userDiv.innerHTML = `
                    <div class="user-status"></div>
                    <div>${user}</div>
                `;
                userList.appendChild(userDiv);
            });
        }
        
        function updateTypingIndicator(users) {
            const indicator = document.getElementById('typingIndicator');
            if (users.length === 0) {
                indicator.style.display = 'none';
            } else {
                indicator.style.display = 'block';
                const userList = users.join(', ');
                indicator.textContent = `${userList} đang gõ...`;
            }
        }
        
        // Socket event handlers
        socket.on('nickname_accepted', function(data) {
            nickname = data.nickname;
            document.getElementById('joinSection').style.display = 'none';
            document.getElementById('chatSection').style.display = 'flex';
            document.getElementById('messageInput').focus();
            
            // Check notification permission
            if ("Notification" in window && Notification.permission === "default") {
                document.getElementById('notificationPermission').style.display = 'block';
            }
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
        
        socket.on('typing_users', function(data) {
            updateTypingIndicator(data.users);
        });
        
        socket.on('message_read_update', function(data) {
            const messageElement = document.querySelector(`[data-message-id="${data.message_id}"]`);
            if (messageElement) {
                const readStatus = messageElement.querySelector('.read-status');
                if (readStatus) {
                    readStatus.textContent = `${data.read_count} người đã xem`;
                }
            }
        });
        
        socket.on('connect', function() {
            console.log('✅ Đã kết nối tới server (SSL Fixed)');
        });
        
        socket.on('disconnect', function() {
            console.log('❌ Mất kết nối tới server');
        });
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initEmojiPicker();
            initThemeSystem();
            loadSavedCustomTheme();
            document.getElementById('nicknameInput').focus();
            document.getElementById('messageInput').addEventListener('keypress', handleKeyPress);
            document.getElementById('nicknameInput').addEventListener('keypress', handleKeyPress);
            
            // Close emoji picker when clicking outside
            document.addEventListener('click', function(e) {
                const picker = document.getElementById('emojiPicker');
                const emojiBtn = e.target.closest('.btn-warning');
                if (!picker.contains(e.target) && !emojiBtn) {
                    picker.style.display = 'none';
                }
            });
        });
    </script>
</body>
</html>
    '''


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(upload_dir, filename)


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print(f"✅ Client connected: {request.sid}")
    log_event(f"Client connected: {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    session_id = request.sid

    with clients_lock:
        if session_id in clients:
            nickname = clients[session_id]['nickname']

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

            # Update typing indicator
            emit_typing_update()

    print(f"❌ Client disconnected: {session_id}")


@socketio.on('set_nickname')
def handle_set_nickname(data):
    """Handle nickname setting with Vietnamese support."""
    session_id = request.sid
    proposed_nickname = data.get('nickname', '').strip()

    if validate_nickname(proposed_nickname):
        # Set nickname
        with clients_lock:
            clients[session_id] = {
                'nickname': proposed_nickname,
                'join_time': datetime.datetime.now().isoformat(),
                'last_seen': datetime.datetime.now().isoformat(),
                'typing': False
            }
            nicknames.add(proposed_nickname)

        # Send confirmation
        emit('nickname_accepted', {'nickname': proposed_nickname})

        # Log join event
        log_event(f"User joined: {proposed_nickname}")

        # Notify other users
        socketio.emit('message', {
            "type": "system",
            "message": f"🎉 {proposed_nickname} đã tham gia phòng chat",
            "timestamp": datetime.datetime.now().isoformat()
        }, include_self=False)

        # Send user list to all clients
        with clients_lock:
            socketio.emit('user_list', {"users": list(nicknames)})

    else:
        emit('nickname_error', {
            'message': 'Nickname không hợp lệ hoặc đã được sử dụng. Vui lòng chọn nickname khác (có thể dùng tiếng Việt có dấu).'
        })


@socketio.on('send_message')
def handle_send_message(data):
    """Handle incoming messages with image support."""
    session_id = request.sid

    with clients_lock:
        if session_id not in clients:
            return
        nickname = clients[session_id]['nickname']

    message_type = data.get('type', 'text')
    timestamp = datetime.datetime.now().isoformat()
    message_id = str(uuid.uuid4())

    if message_type == 'text':
        content = data.get('content', '').strip()
        if content:
            # Create broadcast message
            broadcast_msg = {
                "id": message_id,
                "type": "text",
                "nickname": nickname,
                "content": content,
                "timestamp": timestamp,
                "reads": 0
            }

            # Store message for read receipts
            messages.append(broadcast_msg)
            message_reads[message_id] = set()

            # Log the message
            log_event(f"[CHAT] {nickname}: {content}")

            # Broadcast to all clients
            socketio.emit('message', broadcast_msg)

    elif message_type == 'image':
        image_data = data.get('content', '')
        file_name = data.get('fileName', f'image_{message_id}.jpg')

        if image_data.startswith('data:image'):
            try:
                # Save image file
                header, encoded = image_data.split(',', 1)
                image_binary = base64.b64decode(encoded)

                # Generate safe filename
                safe_filename = f"{message_id}_{file_name.replace(' ', '_')}"
                file_path = os.path.join(upload_dir, safe_filename)

                with open(file_path, 'wb') as f:
                    f.write(image_binary)

                # Create broadcast message
                broadcast_msg = {
                    "id": message_id,
                    "type": "image",
                    "nickname": nickname,
                    "content": f"/uploads/{safe_filename}",
                    "timestamp": timestamp,
                    "reads": 0
                }

                # Store message for read receipts
                messages.append(broadcast_msg)
                message_reads[message_id] = set()

                # Log the image share
                log_event(f"[IMAGE] {nickname} shared: {file_name}")

                # Broadcast to all clients
                socketio.emit('message', broadcast_msg)

            except Exception as e:
                print(f"❌ Error handling image: {e}")
                emit('error', {'message': 'Lỗi khi xử lý ảnh'})


@socketio.on('typing_start')
def handle_typing_start():
    """Handle typing start."""
    session_id = request.sid
    with clients_lock:
        if session_id in clients:
            clients[session_id]['typing'] = True
    emit_typing_update()


@socketio.on('typing_stop')
def handle_typing_stop():
    """Handle typing stop."""
    session_id = request.sid
    with clients_lock:
        if session_id in clients:
            clients[session_id]['typing'] = False
    emit_typing_update()


def emit_typing_update():
    """Emit typing indicator update."""
    with clients_lock:
        typing_users = [client['nickname']
                        for client in clients.values() if client.get('typing', False)]
    socketio.emit('typing_users', {'users': typing_users})


@socketio.on('mark_read')
def handle_mark_read(data):
    """Handle message read receipt."""
    session_id = request.sid
    message_id = data.get('message_id')

    with clients_lock:
        if session_id in clients and message_id in message_reads:
            user_id = clients[session_id]['nickname']
            message_reads[message_id].add(user_id)

            # Find message author and update read count
            for msg in messages:
                if msg['id'] == message_id:
                    read_count = len(message_reads[message_id])

                    # Emit read update to message author only
                    for sid, client in clients.items():
                        if client['nickname'] == msg['nickname']:
                            socketio.emit('message_read_update', {
                                'message_id': message_id,
                                'read_count': read_count
                            }, room=sid)
                    break


def main():
    """Main function to start the enhanced server."""
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

    # Ensure directories exist
    ensure_directories()

    print("="*70)
    print("🔥 ADVANCED CHAT ROOM SERVER (SSL FIXED)")
    print("="*70)
    print(f"📡 Server đang khởi động trên {host}:{port}")
    print(f"🔧 Backend: Threading (Không dùng eventlet)")
    print(f"🛡️ SSL Issues: FIXED ✅")
    print(f"🌐 Truy cập chat tại: http://103.149.252.221:{port}/")
    print(f"🏠 Truy cập local: http://localhost:{port}/")
    print()
    print("✨ Tính năng đầy đủ:")
    print("   🎨 Giao diện hiện đại")
    print("   😊 Emoji và sticker")
    print("   📷 Gửi và chia sẻ ảnh")
    print("   🇻🇳 Hỗ trợ tiếng Việt có dấu")
    print("   🔔 Thông báo tin nhắn mới")
    print("   👁️ Tính năng 'đã xem'")
    print("   ⌨️ Hiển thị 'đang gõ...'")
    print()
    print("⚡ Sử dụng Ctrl+C để dừng server")
    print("="*70)
    print()

    log_event(f"Advanced chat server (SSL Fixed) started on {host}:{port}")

    try:
        # Start the server
        socketio.run(app, host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\n🔴 Đang tắt server...")
        log_event("Advanced chat server shutting down")
    except Exception as e:
        print(f"❌ Lỗi server: {e}")
        log_event(f"Server error: {e}")


if __name__ == "__main__":
    main()
