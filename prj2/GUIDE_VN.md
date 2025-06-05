# 📱 Phòng Chat Mạng Nội Bộ - Hướng Dẫn Sử Dụng (Tiếng Việt)

## 🚀 Hướng Dẫn Nhanh

### Bước 1: Cài Đặt Python
Đảm bảo bạn đã cài Python 3.7 hoặc mới hơn trên máy tính.

**Kiểm tra Python đã cài chưa:**
```bash
python --version
```

**Nếu chưa có Python:**
- Windows: Tải từ [python.org](https://python.org)
- Mac: `brew install python3` hoặc tải từ python.org
- Linux: `sudo apt install python3 python3-pip` (Ubuntu/Debian)

### Bước 2: Cài Đặt Thư Viện
Mở terminal/command prompt trong thư mục dự án và chạy:
```bash
pip install -r requirements.txt
```

### Bước 3: Khởi Chạy Ứng Dụng

**🎯 Cách Dễ (Khuyến nghị để thử nghiệm):**
```bash
python run_demo.py
```
Chọn tùy chọn 3 để tự động khởi chạy cả server và client.

**🔧 Cách Thủ Công:**

**Khởi chạy Server (Máy chủ):**
```bash
python chat_server.py
```

**Khởi chạy Client (Máy khách):**
```bash
python chat_client.py
```

## 📋 Hướng Dẫn Thiết Lập Chi Tiết

### 🖥️ Thiết Lập Server (Máy Chủ)

1. **Chọn Máy Chủ**
   - Máy này sẽ chạy chat server
   - Nên là máy ổn định và luôn kết nối mạng
   - Tất cả người dùng khác sẽ kết nối đến máy này

2. **Tìm Địa Chỉ IP**
   
   **Windows:**
   ```cmd
   ipconfig
   ```
   Tìm "IPv4 Address" (thường bắt đầu bằng 192.168.x.x hoặc 10.x.x.x)

   **Mac/Linux:**
   ```bash
   ifconfig
   # hoặc
   ip addr show
   ```

3. **Cấu Hình Firewall (Quan Trọng!)**
   
   **Windows:**
   - Mở "Windows Defender Firewall"
   - Nhấp "Allow an app or feature through Windows Defender Firewall"
   - Nhấp "Change Settings" → "Allow another app"
   - Duyệt và thêm Python.exe
   - Tích cả ô "Private" và "Public"

   **Mac:**
   ```bash
   sudo /usr/libexec/ApplicationFirewall/socketfilterfw --add python3
   ```

   **Linux:**
   ```bash
   sudo ufw allow 12345
   ```

4. **Khởi Chạy Server**
   ```bash
   python chat_server.py
   ```
   
   Bạn sẽ thấy:
   ```
   Chat server started on localhost:12345
   Logs will be saved to: chat_logs
   ```

5. **Chia Sẻ Địa Chỉ IP**
   - Cho người dùng khác biết địa chỉ IP máy bạn (từ bước 2)
   - Chia sẻ số port (mặc định: 12345)

### 💻 Thiết Lập Client (Máy Khách)

1. **Lấy Thông Tin Kết Nối**
   - Địa chỉ IP của server (từ máy chủ)
   - Số port (mặc định: 12345)

2. **Khởi Chạy Client**
   ```bash
   python chat_client.py
   ```

3. **Kết Nối Đến Server**
   - Nhập địa chỉ IP của server
   - Nhập số port (12345)
   - Nhấp "Connect"

4. **Chọn Nickname**
   - Nhập nickname duy nhất (1-20 ký tự)
   - Chỉ dùng chữ cái, số, khoảng trắng và dấu câu cơ bản
   - Nickname phải là duy nhất (chưa ai dùng)

5. **Bắt Đầu Chat!**
   - Gõ tin nhắn và nhấn Enter
   - Sử dụng nút emoji, sticker và hình ảnh
   - Xem người dùng khác ở panel bên phải

## 🎮 Cách Sử Dụng Tính Năng

### 💬 Tin Nhắn Văn Bản
- Gõ tin nhắn trong ô nhập ở phía dưới
- Nhấn `Enter` hoặc nút "Send"
- Tin nhắn hiển thị với thời gian và tên người gửi
- Người khác thấy tin nhắn của bạn ngay lập tức

### 😀 Emoji
- Nhấp nút "😀 Emoji"
- Duyệt qua hơn 80 emoji có sẵn
- Nhấp emoji nào đó để gửi ngay
- Emoji hiển thị lớn hơn và màu cam

### 🎭 Sticker
- Nhấp nút "🎭 Sticker"
- Chọn từ các sticker văn bản có sẵn:
  - happy (vui): ヽ(°〇°)ﾉ
  - love (yêu): (♡°▽°♡)
  - cool (ngầu): ( ͡° ͜ʖ ͡°)
  - surprised (ngạc nhiên): (⊙_⊙)
  - sad (buồn): (╥﹏╥)
  - angry (tức giận): (╬ಠ益ಠ)
  - party (tiệc tung): \\(^o^)/
  - sleepy (buồn ngủ): (-.-)zzZ
  - confused (bối rối): (´･ω･`)
- Nhấp sticker nào đó để gửi

### 🖼️ Chia Sẻ Hình Ảnh
- Nhấp nút "🖼️ Image"
- Chọn file ảnh từ máy tính
- **Định dạng hỗ trợ:** PNG, JPG, JPEG, GIF, BMP
- **Kích thước tối đa:** 1MB mỗi ảnh
- Ảnh hiển thị dạng thumbnail trong chat
- Nhấp vào ảnh để xem to hơn

### 👥 Danh Sách Người Dùng
- Xem tất cả người dùng đang online ở panel bên phải
- Danh sách tự động cập nhật khi có người vào/ra
- Nickname của bạn cũng xuất hiện trong danh sách
- Người dùng được sắp xếp theo thứ tự alphabet

### 📊 Tin Nhắn Hệ Thống
- Văn bản màu xanh in nghiêng hiển thị thông báo hệ thống:
  - "Welcome, [nickname]!" khi bạn vào
  - "[User] joined the chat" khi có người kết nối
  - "[User] left the chat" khi có người ngắt kết nối
  - Thông báo trạng thái kết nối

## 🌐 Ví Dụ Thiết Lập Mạng

### Ví Dụ 1: Mạng Gia Đình
**Tình huống:** Thành viên gia đình chat ở nhà

1. **Thiết lập Router:** Hầu hết router gia đình dùng 192.168.1.x hoặc 192.168.0.x
2. **Máy Chủ:** Khởi chạy server (ví dụ: 192.168.1.100)
3. **Thiết bị khác:** Kết nối điện thoại, tablet, laptop vào cùng WiFi
4. **Kết nối:** Dùng 192.168.1.100:12345 để kết nối

### Ví Dụ 2: Mạng Văn Phòng
**Tình huống:** Đồng nghiệp chat trong văn phòng

1. **Quản trị mạng:** Có thể cần cho phép port 12345
2. **Máy Chủ:** Dùng IP văn phòng (ví dụ: 10.0.1.50)
3. **Đồng nghiệp:** Kết nối bằng 10.0.1.50:12345
4. **Lưu ý:** Kiểm tra chính sách IT công ty trước

### Ví Dụ 3: Trường Học/Đại Học
**Tình huống:** Sinh viên trong phòng máy

1. **Mạng Lab:** Thường dùng dải IP riêng
2. **Máy Chủ:** Tìm IP bằng `ipconfig` hoặc `ifconfig`
3. **Máy khác:** Kết nối đến IP của máy chủ
4. **Port:** Mặc định 12345 (có thể cần quyền admin)

## 🔧 Khắc Phục Sự Cố

### ❌ Lỗi Kết Nối Thường Gặp

**"Connection refused" hoặc "Can't connect"**
- ✅ Kiểm tra server có đang chạy trên máy chủ không
- ✅ Xác minh địa chỉ IP đúng chưa
- ✅ Xác nhận số port (mặc định: 12345)
- ✅ Kiểm tra cài đặt firewall trên máy chủ
- ✅ Đảm bảo cả hai máy cùng mạng

**"Nickname already taken" (Nickname đã được dùng)**
- ✅ Chọn nickname khác
- ✅ Nhờ người dùng hiện tại ngắt kết nối trước
- ✅ Thêm số hoặc ký tự để tạo tên duy nhất

**Server không khởi chạy được**
- ✅ Kiểm tra port 12345 có đang được dùng không
- ✅ Thử port khác: `python chat_server.py localhost 12346`
- ✅ Chạy với quyền administrator nếu cần

### 🖼️ Lỗi Hình Ảnh

**Hình ảnh không hiển thị**
- ✅ Cài Pillow: `pip install Pillow`
- ✅ Kiểm tra kích thước ảnh (phải dưới 1MB)
- ✅ Dùng định dạng hỗ trợ: PNG, JPG, JPEG, GIF, BMP
- ✅ Thử file ảnh khác

**Lỗi "Image too large" (Ảnh quá lớn)**
- ✅ Giảm kích thước ảnh trước khi gửi
- ✅ Dùng công cụ nén ảnh
- ✅ Tối đa cho phép: 1MB (1.024 KB)

### 🔌 Lỗi Mạng

**Không tìm được IP server**
```bash
# Windows
ipconfig | findstr IPv4

# Mac/Linux  
ifconfig | grep "inet "
```

**Firewall chặn kết nối**
- ✅ Thêm Python vào ngoại lệ firewall
- ✅ Cho phép port 12345 trong quy tắc firewall
- ✅ Tạm thời tắt firewall để test

**Subnet mạng khác nhau**
- ✅ Đảm bảo tất cả thiết bị cùng mạng WiFi
- ✅ Kiểm tra mạng có bật client isolation không
- ✅ Liên hệ quản trị mạng nếu cần

## 📝 Log Server

Server tự động tạo log chi tiết trong thư mục `chat_logs`:

**Định dạng file log:** `chat_log_YYYYMMDD.txt`

**Nội dung được ghi log:**
- Sự kiện khởi động/tắt server
- Kết nối người dùng với địa chỉ IP
- Ngắt kết nối người dùng
- Tất cả tin nhắn văn bản
- Sử dụng emoji và sticker
- Sự kiện chia sẻ ảnh
- Thông báo lỗi

**Ví dụ các dòng log:**
```
[2024-01-15 14:30:25] Chat server started on localhost:12345
[2024-01-15 14:30:45] User joined: Alice from 192.168.1.101:52341
[2024-01-15 14:31:02] [CHAT] Alice: Xin chào mọi người!
[2024-01-15 14:31:15] [EMOJI] Bob: 😀
[2024-01-15 14:31:30] [IMAGE] Alice: vacation.jpg
[2024-01-15 14:32:10] User left: Bob
```

## ⚠️ Lưu Ý Quan Trọng

### 🔒 Bảo Mật
- Ứng dụng này được thiết kế cho **mạng nội bộ only**
- **Không mã hóa** - tin nhắn gửi dạng văn bản thuần
- **Không xác thực** ngoài nickname
- Không sử dụng qua internet công cộng mà không có VPN

### 🎯 Hiệu Suất
- **Khuyến nghị:** 5-10 người dùng đồng thời
- **Lịch sử chat** không được lưu (mất khi server tắt)
- **File log** tăng theo thời gian - nên lưu trữ định kỳ
- **Giới hạn ảnh:** 1MB mỗi ảnh để hiệu suất tốt

### 💾 Dữ Liệu
- Tin nhắn chat **không lưu trữ** (mất khi server dừng)
- Chỉ log hoạt động được lưu vào file
- Không có tài khoản người dùng hoặc mật khẩu
- Không thể lấy lại lịch sử tin nhắn

## 🆘 Nhận Hỗ Trợ

Nếu gặp vấn đề:

1. **Kiểm tra output console** để tìm thông báo lỗi
2. **Xem lại file log** trong thư mục `chat_logs`
3. **Xác minh kết nối mạng** bằng lệnh ping
4. **Test với firewall tắt** tạm thời
5. **Thử số port khác** nếu 12345 bị chặn
6. **Khởi động lại server và client** để reset kết nối

## 📞 Lệnh Hỗ Trợ

**Test kết nối mạng:**
```bash
# Ping máy server
ping [địa-chỉ-ip-server]

# Kiểm tra port có mở không (Windows)
telnet [ip-server] 12345

# Kiểm tra port có mở không (Mac/Linux)
nc -zv [ip-server] 12345
```

**Sử dụng port khác:**
```bash
# Khởi chạy server với port khác
python chat_server.py localhost 8080

# Client kết nối đến port 8080
# (Nhập 8080 trong ô port)
```

## 🎯 Mẹo Sử Dụng

### 📱 Kết Nối Điện Thoại
- Cài Python app như Pydroid 3 (Android)
- Kết nối điện thoại cùng WiFi với máy chủ
- Chạy client trên điện thoại

### 🏠 Gia Đình
- Đặt máy chủ ở vị trí trung tâm có WiFi tốt
- Chia sẻ IP và port cho tất cả thành viên
- Tạo nickname theo tên thật để dễ nhận biết

### 🏢 Văn Phòng
- Xin phép IT trước khi sử dụng
- Kiểm tra chính sách mạng công ty
- Không gửi thông tin nhạy cảm

### 🎓 Trường Học
- Chỉ dùng trong môi trường học tập
- Tuân thủ quy định sử dụng mạng trường
- Không làm ảnh hưởng đến học tập

## 🔍 Debug Nâng Cao

### Kiểm Tra Chi Tiết Mạng

**Xem tất cả interface mạng:**
```bash
# Windows
ipconfig /all

# Mac/Linux
ip addr show
ifconfig -a
```

**Kiểm tra routing:**
```bash
# Windows
route print

# Mac/Linux
ip route
route -n
```

### Test Kết Nối

**Test TCP connection:**
```bash
# Windows (nếu có telnet)
telnet [ip-server] 12345

# Mac/Linux
nc -zv [ip-server] 12345
telnet [ip-server] 12345
```

**Kiểm tra port đang dùng:**
```bash
# Windows
netstat -an | findstr 12345

# Mac/Linux
netstat -an | grep 12345
lsof -i :12345
```

---

## 🎉 Chúc Bạn Chat Vui Vẻ!

Phòng Chat Mạng Nội Bộ của bạn đã sẵn sàng sử dụng. Hãy vui vẻ giao tiếp bằng văn bản, emoji, sticker và hình ảnh trên mạng nội bộ!

**Chúc Chat Vui!** 💬✨

---

## 📞 Liên Hệ & Hỗ Trợ

Nếu cần hỗ trợ thêm:
- Kiểm tra file README.md (tiếng Anh) để biết thêm chi tiết kỹ thuật
- Xem file chat_plan.md để hiểu kế hoạch phát triển
- Kiểm tra source code trong chat_server.py và chat_client.py 