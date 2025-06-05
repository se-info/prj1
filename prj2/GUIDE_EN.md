# 📱 Local Network Chat Room - User Guide (English)

## 🚀 Quick Start Guide

### Step 1: Install Python
Make sure you have Python 3.7 or newer installed on your computer.

**Check if Python is installed:**
```bash
python --version
```

**If Python is not installed:**
- Windows: Download from [python.org](https://python.org)
- Mac: `brew install python3` or download from python.org
- Linux: `sudo apt install python3 python3-pip` (Ubuntu/Debian)

### Step 2: Install Dependencies
Open terminal/command prompt in the project folder and run:
```bash
pip install -r requirements.txt
```

### Step 3: Start the Application

**🎯 Easy Way (Recommended for Testing):**
```bash
python run_demo.py
```
Choose option 3 to start both server and client automatically.

**🔧 Manual Way:**

**Start the Server (Host Computer):**
```bash
python chat_server.py
```

**Start the Client (Any Computer):**
```bash
python chat_client.py
```

## 📋 Detailed Setup Instructions

### 🖥️ Setting Up the Server (Host Computer)

1. **Choose the Host Computer**
   - This computer will run the chat server
   - Should be stable and remain connected to the network
   - All other users will connect to this computer

2. **Find Your IP Address**
   
   **Windows:**
   ```cmd
   ipconfig
   ```
   Look for "IPv4 Address" (usually starts with 192.168.x.x or 10.x.x.x)

   **Mac/Linux:**
   ```bash
   ifconfig
   # or
   ip addr show
   ```

3. **Configure Firewall (Important!)**
   
   **Windows:**
   - Open "Windows Defender Firewall"
   - Click "Allow an app or feature through Windows Defender Firewall"
   - Click "Change Settings" → "Allow another app"
   - Browse and add Python.exe
   - Check both "Private" and "Public" boxes

   **Mac:**
   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add python3
   ```

   **Linux:**
   ```bash
   sudo ufw allow 12345
   ```

4. **Start the Server**
   ```bash
   python chat_server.py
   ```
   
   You should see:
   ```
   Chat server started on localhost:12345
   Logs will be saved to: chat_logs
   ```

5. **Share Your IP Address**
   - Tell other users your computer's IP address (from step 2)
   - Share the port number (default: 12345)

### 💻 Setting Up Clients (User Computers)

1. **Get Connection Information**
   - Server IP address (from host computer)
   - Port number (default: 12345)

2. **Start the Client**
   ```bash
   python chat_client.py
   ```

3. **Connect to Server**
   - Enter the server IP address
   - Enter the port number (12345)
   - Click "Connect"

4. **Choose Your Nickname**
   - Enter a unique nickname (1-20 characters)
   - Use letters, numbers, spaces, and basic punctuation only
   - Nickname must be unique (not used by another user)

5. **Start Chatting!**
   - Type messages and press Enter
   - Use emoji, stickers, and image buttons
   - See other users in the right panel

## 🎮 How to Use Features

### 💬 Text Messaging
- Type your message in the input field at the bottom
- Press `Enter` or click "Send" button
- Messages appear with timestamp and your nickname
- Other users see your messages in real-time

### 😀 Emojis
- Click the "😀 Emoji" button
- Browse through 80+ available emojis
- Click any emoji to send it immediately
- Emojis appear larger and in orange color

### 🎭 Stickers
- Click the "🎭 Sticker" button
- Choose from predefined text-based stickers:
  - happy: ヽ(°〇°)ﾉ
  - love: (♡°▽°♡)
  - cool: ( ͡° ͜ʖ ͡°)
  - surprised: (⊙_⊙)
  - sad: (╥﹏╥)
  - angry: (╬ಠ益ಠ)
  - party: \\(^o^)/
  - sleepy: (-.-)zzZ
  - confused: (´･ω･`)
- Click any sticker to send it

### 🖼️ Image Sharing
- Click the "🖼️ Image" button
- Select an image file from your computer
- **Supported formats:** PNG, JPG, JPEG, GIF, BMP
- **Maximum size:** 1MB per image
- Images appear as thumbnails in the chat
- Click on images to view them larger

### 👥 User List
- See all connected users in the right panel
- List updates automatically when users join/leave
- Your own nickname appears in the list
- Users are sorted alphabetically

### 📊 System Messages
- Blue italic text shows system notifications:
  - "Welcome, [nickname]!" when you join
  - "[User] joined the chat" when someone connects
  - "[User] left the chat" when someone disconnects
  - Connection status messages

## 🌐 Network Setup Examples

### Example 1: Home Network
**Scenario:** Family members chatting at home

1. **Router Setup:** Most home routers use 192.168.1.x or 192.168.0.x
2. **Host Computer:** Start server (e.g., 192.168.1.100)
3. **Other Devices:** Connect phones, tablets, laptops to same WiFi
4. **Connect:** Use 192.168.1.100:12345 to connect

### Example 2: Office Network
**Scenario:** Colleagues chatting in the office

1. **Network Admin:** May need to allow port 12345
2. **Host Computer:** Use office IP (e.g., 10.0.1.50)
3. **Colleagues:** Connect using 10.0.1.50:12345
4. **Note:** Check company IT policies first

### Example 3: School/University
**Scenario:** Students in computer lab

1. **Lab Network:** Usually uses private IP ranges
2. **Host Computer:** Find IP with `ipconfig` or `ifconfig`
3. **Other Computers:** Connect to host's IP address
4. **Port:** Default 12345 (may need admin permission)

## 🔧 Troubleshooting

### ❌ Common Connection Problems

**"Connection refused" or "Can't connect"**
- ✅ Check if server is running on host computer
- ✅ Verify IP address is correct
- ✅ Confirm port number (default: 12345)
- ✅ Check firewall settings on host computer
- ✅ Ensure both computers are on same network

**"Nickname already taken"**
- ✅ Choose a different nickname
- ✅ Ask current user to disconnect first
- ✅ Add numbers or characters to make it unique

**Server won't start**
- ✅ Check if port 12345 is already in use
- ✅ Try a different port: `python chat_server.py localhost 12346`
- ✅ Run as administrator if needed

### 🖼️ Image Problems

**Images not displaying**
- ✅ Install Pillow: `pip install Pillow`
- ✅ Check image size (must be under 1MB)
- ✅ Use supported formats: PNG, JPG, JPEG, GIF, BMP
- ✅ Try a different image file

**"Image too large" error**
- ✅ Resize image before sending
- ✅ Use image compression tools
- ✅ Maximum allowed: 1MB (1,024 KB)

### 🔌 Network Issues

**Can't find server IP**
```bash
# Windows
ipconfig | findstr IPv4

# Mac/Linux  
ifconfig | grep "inet "
```

**Firewall blocking connection**
- ✅ Add Python to firewall exceptions
- ✅ Allow port 12345 in firewall rules
- ✅ Temporarily disable firewall to test

**Different network subnets**
- ✅ Ensure all devices on same WiFi network
- ✅ Check if network has client isolation enabled
- ✅ Contact network administrator if needed

## 📝 Server Logs

The server automatically creates detailed logs in the `chat_logs` folder:

**Log file format:** `chat_log_YYYYMMDD.txt`

**What gets logged:**
- Server start/stop events
- User connections with IP addresses
- User disconnections
- All text messages
- Emoji and sticker usage
- Image sharing events
- Error messages

**Example log entries:**
```
[2024-01-15 14:30:25] Chat server started on localhost:12345
[2024-01-15 14:30:45] User joined: Alice from 192.168.1.101:52341
[2024-01-15 14:31:02] [CHAT] Alice: Hello everyone!
[2024-01-15 14:31:15] [EMOJI] Bob: 😀
[2024-01-15 14:31:30] [IMAGE] Alice: vacation.jpg
[2024-01-15 14:32:10] User left: Bob
```

## ⚠️ Important Notes

### 🔒 Security
- This application is designed for **local networks only**
- **No encryption** - messages are sent in plain text
- **No authentication** beyond nicknames
- Do not use over public internet without VPN

### 🎯 Performance
- **Recommended:** 5-10 concurrent users
- **Chat history** is not saved (clears when server restarts)
- **Log files** grow over time - archive them periodically
- **Image limit:** 1MB per image for good performance

### 💾 Data
- Chat messages are **not persistent** (lost when server stops)
- Only activity logs are saved to files
- No user accounts or passwords
- No message history retrieval

## 🆘 Getting Help

If you encounter issues:

1. **Check the console output** for error messages
2. **Review the log files** in `chat_logs` folder
3. **Verify network connectivity** with ping tests
4. **Test with firewall disabled** temporarily
5. **Try different port numbers** if 12345 is blocked
6. **Restart the server and clients** to reset connections

## 📞 Support Commands

**Test network connectivity:**
```bash
# Ping the server computer
ping [server-ip-address]

# Check if port is open (Windows)
telnet [server-ip] 12345

# Check if port is open (Mac/Linux)
nc -zv [server-ip] 12345
```

**Alternative port usage:**
```bash
# Start server on different port
python chat_server.py localhost 8080

# Client connects to port 8080
# (Enter 8080 in port field)
```

---

## 🎉 Enjoy Chatting!

Your Local Network Chat Room is now ready to use. Have fun communicating with text, emojis, stickers, and images on your local network!

**Happy Chatting!** 💬✨ 