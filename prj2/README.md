# Local Network Chat Room

A feature-rich local network chat application built with Python that allows users to communicate within the same network using text messages, emojis, stickers, and images.

## Features

✅ **Core Chat Functionality**
- Real-time text messaging
- Unique nickname system
- User join/leave notifications
- Online users list

✅ **Rich Media Support**
- Emoji picker with 80+ emojis
- Predefined sticker collection
- Image sharing (PNG, JPG, GIF, BMP)
- Image thumbnails in chat

✅ **User Management**
- Nickname validation and uniqueness
- Real-time user list updates
- Connection status tracking

✅ **Activity Logging**
- Daily log files with timestamps
- User join/leave events
- All chat messages and media
- Automatic log rotation by date

✅ **Modern GUI**
- Clean Tkinter interface
- Resizable windows
- Scrollable chat area
- Status indicators

## Requirements

- Python 3.7+
- Pillow (PIL) for image handling
- Tkinter (usually included with Python)

## Installation

1. **Clone or download the project files:**
   ```
   chat_server.py
   chat_client.py
   requirements.txt
   README.md
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Quick Start

### Starting the Server

1. **Run the server on the host machine:**
   ```bash
   python chat_server.py
   ```
   
   Or specify custom host/port:
   ```bash
   python chat_server.py 192.168.1.100 12345
   ```

2. **The server will:**
   - Listen for client connections
   - Create a `chat_logs` directory
   - Generate daily log files (format: `chat_log_YYYYMMDD.txt`)
   - Display connection status in the console

### Connecting Clients

1. **Run the client on any machine in the network:**
   ```bash
   python chat_client.py
   ```

2. **Connection steps:**
   - Enter the server IP address (where the server is running)
   - Enter the port number (default: 12345)
   - Click "Connect"
   - Enter a unique nickname when prompted
   - Start chatting!

## Usage Guide

### Text Messages
- Type your message in the input field
- Press Enter or click "Send" to send
- Messages appear with timestamps and sender names

### Emojis
- Click the "😀 Emoji" button
- Select from 80+ available emojis
- Emojis are sent immediately when selected

### Stickers
- Click the "🎭 Sticker" button
- Choose from predefined text-based stickers
- Includes various emotions and expressions

### Images
- Click the "🖼️ Image" button
- Select an image file (max 1MB)
- Supported formats: PNG, JPG, JPEG, GIF, BMP
- Images appear as thumbnails in the chat

### User List
- View all connected users in the right panel
- Updates automatically when users join/leave
- Shows current online status

## Network Configuration

### Finding Your Server IP

**Windows:**
```cmd
ipconfig
```
Look for "IPv4 Address" under your network adapter.

**Mac/Linux:**
```bash
ifconfig
# or
ip addr show
```

### Firewall Settings

Make sure the server port (default 12345) is not blocked by firewall rules on the host machine.

**Windows Firewall:**
1. Open Windows Defender Firewall
2. Click "Allow an app through firewall"
3. Add Python or the specific port

**Mac:**
```bash
sudo pfctl -f /etc/pf.conf
```

**Linux (ufw):**
```bash
sudo ufw allow 12345
```

## File Structure

```
prj2/
├── chat_server.py      # Server application
├── chat_client.py      # Client GUI application  
├── requirements.txt    # Python dependencies
├── README.md          # This file
├── chat_plan.md       # Development plan
└── chat_logs/         # Generated log directory
    └── chat_log_YYYYMMDD.txt
```

## Log Files

The server automatically creates detailed logs in the `chat_logs` directory:

**Log entries include:**
- Server start/stop events
- User join/leave with IP addresses
- All chat messages with timestamps
- Emoji and sticker usage
- Image sharing events
- Error conditions

**Example log entry:**
```
[2024-01-15 14:30:25] User joined: Alice from 192.168.1.101:52341
[2024-01-15 14:30:45] [CHAT] Alice: Hello everyone!
[2024-01-15 14:31:02] [EMOJI] Bob: 😀
[2024-01-15 14:31:15] [IMAGE] Alice: vacation.jpg
[2024-01-15 14:32:10] User left: Bob
```

## Troubleshooting

### Common Issues

**"Connection refused" error:**
- Check if the server is running
- Verify the IP address and port
- Check firewall settings

**"Nickname already taken":**
- Choose a different nickname
- Wait if someone just disconnected

**Images not displaying:**
- Ensure Pillow is installed: `pip install Pillow`
- Check if image file is under 1MB
- Verify image format is supported

**GUI not appearing:**
- Ensure Tkinter is installed (usually comes with Python)
- Try running with `python -m tkinter` to test

### Performance Notes

- Recommended for 5-10 concurrent users
- Image files are limited to 1MB for performance
- Chat history is not persistent (clears on server restart)
- Log files grow over time and should be archived periodically

## Development

This project follows the development plan outlined in `chat_plan.md`. Key phases completed:

- ✅ Phase 0: Core networking and basic messaging
- ✅ Phase 1: Multi-user chat and logging  
- ✅ Phase 2: Rich media support (emojis, stickers, images)
- ✅ Phase 3: UI polish and error handling

## Technical Details

**Architecture:**
- Client-server model using TCP sockets
- JSON message protocol
- Multi-threaded server handling
- Event-driven GUI with Tkinter

**Security Notes:**
- No encryption (local network use only)
- No authentication beyond nicknames
- File size limits to prevent abuse
- Input validation for nicknames and messages

## License

This project is provided as-is for educational and local network use.

---

**Happy Chatting! 🎉** 