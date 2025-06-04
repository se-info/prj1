# Hướng Dẫn Sử Dụng Ứng Dụng Phát Hiện Order Block Cryptocurrency

Ứng dụng web tiên tiến để tự động phát hiện và hiển thị Order Blocks (OBs) trên biểu đồ giá cryptocurrency sử dụng nguyên lý Smart Money Concepts (SMC).

## 📋 Mục Lục

1. [Tính Năng Chính](#tính-năng-chính)
2. [Cài Đặt và Thiết Lập](#cài-đặt-và-thiết-lập)
3. [Hướng Dẫn Sử Dụng](#hướng-dẫn-sử-dụng)
4. [Truy Cập Qua IP Tĩnh và Mạng](#truy-cập-qua-ip-tĩnh-và-mạng)
5. [Triển Khai Lên Hosting](#triển-khai-lên-hosting)
6. [Giải Thích Thuật Toán](#giải-thích-thuật-toán)
7. [Khắc Phục Sự Cố](#khắc-phục-sự-cố)
8. [Câu Hỏi Thường Gặp](#câu-hỏi-thường-gặp)

## 🚀 Tính Năng Chính

- **📊 Dữ Liệu Real-time**: Kết nối API Binance để lấy dữ liệu cryptocurrency trực tiếp
- **🎯 Phát Hiện Order Block**: Tự động nhận diện Order Blocks tăng và giảm
- **📈 Break of Structure (BOS)**: Phát hiện và hiển thị các điểm phá vỡ cấu trúc thị trường
- **📱 Giao Diện Hiện Đại**: Thiết kế dark theme với hiệu ứng glass morphism
- **⏰ Đa Khung Thời Gian**: Hỗ trợ 15 phút, 1 giờ, 4 giờ, 1 ngày
- **💰 50+ Cặp Coin**: Phân tích các cặp USDT phổ biến
- **📊 Biểu Đồ Tương Tác**: Sử dụng Plotly để tạo biểu đồ nến đẹp mắt
- **📱 Responsive**: Hoạt động tốt trên máy tính, tablet và điện thoại

## 💻 Cài Đặt và Thiết Lập

### Yêu Cầu Hệ Thống

- **Python**: Phiên bản 3.11.7 trở lên
- **RAM**: Tối thiểu 2GB
- **Dung lượng**: 500MB trống
- **Internet**: Kết nối ổn định để lấy dữ liệu

### Phương Pháp 1: Cài Đặt Nhanh (Windows)

1. **Tải về tất cả files** vào một thư mục
2. **Chạy file `start.bat`** bằng cách double-click
3. **Đợi cài đặt hoàn tất** (khoảng 2-3 phút)
4. **Mở trình duyệt** và truy cập `http://localhost:5000`

### Phương Pháp 2: Cài Đặt Thủ Công

```bash
# Bước 1: Tạo virtual environment (khuyến nghị)
python -m venv venv

# Bước 2: Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Bước 3: Cài đặt các thư viện cần thiết
pip install -r requirements.txt

# Bước 4: Chạy ứng dụng
python app.py
```

### Kiểm Tra Cài Đặt

Sau khi chạy thành công, bạn sẽ thấy:
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[your-ip]:5000
```

## 📖 Hướng Dẫn Sử Dụng

### Bước 1: Truy Cập Ứng Dụng

Mở trình duyệt và vào địa chỉ: `http://localhost:5000`

### Bước 2: Chọn Cặp Coin

1. Trong phần **"Analysis Settings"**
2. Chọn **"Trading Pair"** (ví dụ: BTC/USDT, ETH/USDT)
3. Ứng dụng sẽ tự động tải 50+ cặp coin phổ biến

### Bước 3: Chọn Khung Thời Gian

Chọn một trong các khung thời gian:
- **15m**: Phù hợp cho scalping
- **1h**: Tốt cho day trading (mặc định)
- **4h**: Phù hợp cho swing trading
- **1d**: Dành cho phân tích dài hạn

### Bước 4: Phân Tích

1. Click nút **"Analyze Order Blocks"**
2. Đợi 3-5 giây để ứng dụng xử lý dữ liệu
3. Xem kết quả trên biểu đồ và bảng thống kê

### Đọc Hiểu Biểu Đồ

#### Màu Sắc và Ký Hiệu:
- **🟢 Hình chữ nhật xanh**: Bullish Order Block (vùng mua)
- **🔴 Hình chữ nhật đỏ**: Bearish Order Block (vùng bán)
- **🔺 Tam giác xanh**: Bullish BOS (phá vỡ cấu trúc tăng)
- **🔻 Tam giác đỏ**: Bearish BOS (phá vỡ cấu trúc giảm)

#### Thông Tin Thống Kê:
- **Bullish OBs**: Số lượng Order Block tăng được phát hiện
- **Bearish OBs**: Số lượng Order Block giảm được phát hiện
- **Bullish BOS**: Số điểm phá vỡ cấu trúc tăng
- **Bearish BOS**: Số điểm phá vỡ cấu trúc giảm

## 🌐 Truy Cập Qua IP Tĩnh và Mạng

### Cấu Hình Để Truy Cập Từ Các Máy Khác

Mặc định, ứng dụng đã được cấu hình để chạy trên `0.0.0.0:5000`, có nghĩa là có thể truy cập từ bất kỳ IP nào trong mạng.

#### 1. Kiểm Tra IP Của Máy Chủ

**Windows:**
```cmd
ipconfig
# Tìm dòng "IPv4 Address" 
# Ví dụ: 192.168.1.100
```

**Mac/Linux:**
```bash
ifconfig
# hoặc
ip addr show
# Tìm IP trong dải 192.168.x.x hoặc 10.x.x.x
```

#### 2. Truy Cập Từ Các Máy Khác

Sau khi biết IP của máy chủ (ví dụ: `192.168.1.100`), các máy khác trong cùng mạng có thể truy cập:

```
http://192.168.1.100:5000
```

#### 3. Cấu Hình Firewall (Nếu Cần)

**Windows Firewall:**
```cmd
# Mở Command Prompt với quyền Administrator
netsh advfirewall firewall add rule name="Python Flask App" dir=in action=allow protocol=TCP localport=5000
```

**Linux (Ubuntu/Debian):**
```bash
sudo ufw allow 5000
sudo ufw reload
```

**macOS:**
```bash
# Thường không cần cấu hình thêm
# Kiểm tra System Preferences → Security & Privacy → Firewall
```

### Cấu Hình Port Tùy Chỉnh

Nếu muốn đổi port (ví dụ từ 5000 sang 8080), chỉnh sửa file `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Đổi port ở đây
```

### Truy Cập Từ Internet (Nâng Cao)

#### 1. Port Forwarding trên Router

1. Đăng nhập vào router (thường là `192.168.1.1` hoặc `192.168.0.1`)
2. Tìm mục **"Port Forwarding"** hoặc **"Virtual Server"**
3. Thêm rule mới:
   - **Service Name**: Flask App
   - **External Port**: 5000
   - **Internal Port**: 5000
   - **Internal IP**: IP của máy chủ (ví dụ: 192.168.1.100)
   - **Protocol**: TCP

#### 2. Sử dụng Dynamic DNS (Tùy chọn)

Nếu IP công cộng thay đổi thường xuyên, có thể dùng:
- **No-IP**: [noip.com](https://noip.com)
- **DynDNS**: [dyn.com](https://dyn.com)
- **Duck DNS**: [duckdns.org](https://duckdns.org)

#### 3. Bảo Mật Khi Mở Ra Internet

⚠️ **Cảnh báo Bảo Mật:**
```python
# KHÔNG sử dụng debug=True khi mở ra internet
if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
```

### Sử Dụng HTTPS (Khuyến Nghị)

Để bảo mật hơn, có thể thêm SSL certificate:

```python
# Thêm vào app.py
if __name__ == '__main__':
    app.run(
        debug=False, 
        host='0.0.0.0', 
        port=5000,
        ssl_context='adhoc'  # Tự tạo certificate tạm thời
    )
```

Hoặc sử dụng reverse proxy như Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Ví Dụ Cấu Hình Mạng

```
Router (192.168.1.1)
├── Máy chủ Flask (192.168.1.100:5000)
├── Máy tính A (192.168.1.101) → truy cập: http://192.168.1.100:5000
├── Điện thoại B (192.168.1.102) → truy cập: http://192.168.1.100:5000
└── Laptop C (192.168.1.103) → truy cập: http://192.168.1.100:5000
```

### Kiểm Tra Kết Nối

```bash
# Từ máy khác, kiểm tra kết nối tới máy chủ
ping 192.168.1.100

# Kiểm tra port có mở không
telnet 192.168.1.100 5000
# hoặc
nc -zv 192.168.1.100 5000
```

## ☁️ Triển Khai Lên Hosting

### Tự Động với Script

```bash
python deploy.py
```

Chọn từ menu:
1. **Test locally** - Chạy thử trên máy
2. **Deploy to Heroku** - Triển khai lên Heroku
3. **Railway instructions** - Hướng dẫn Railway
4. **Render instructions** - Hướng dẫn Render
5. **Create Docker files** - Tạo file Docker

### Triển Khai Heroku (Miễn Phí)

#### Bước 1: Tạo Tài Khoản
1. Truy cập [heroku.com](https://heroku.com)
2. Đăng ký tài khoản miễn phí
3. Xác thực email

#### Bước 2: Cài Đặt Heroku CLI
1. Tải Heroku CLI từ [devcenter.heroku.com](https://devcenter.heroku.com/articles/heroku-cli)
2. Cài đặt và khởi động lại máy tính
3. Kiểm tra: `heroku --version`

#### Bước 3: Triển Khai
```bash
# 1. Đăng nhập Heroku
heroku login

# 2. Tạo app (thay your-app-name bằng tên bạn muốn)
heroku create your-app-name

# 3. Khởi tạo Git (nếu chưa có)
git init
git add .
git commit -m "Initial commit"

# 4. Deploy
git push heroku main

# 5. Mở app
heroku open
```

### Triển Khai Railway (Đơn Giản)

1. Truy cập [railway.app](https://railway.app)
2. Đăng nhập bằng GitHub
3. Click **"New Project"**
4. Chọn **"Deploy from GitHub repo"**
5. Chọn repository của bạn
6. Railway sẽ tự động phát hiện Python và triển khai

### Triển Khai Render (Ổn Định)

1. Truy cập [render.com](https://render.com)
2. Đăng ký/Đăng nhập
3. Click **"New"** → **"Web Service"**
4. Kết nối GitHub repository
5. Cấu hình:
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
6. Click **"Create Web Service"**

## 🔬 Giải Thích Thuật Toán

### Thuật Toán Phát Hiện Order Block

#### 1. Nhận Diện Swing Points
```python
def find_swing_highs_lows(df, period=5):
    # Tìm swing high: điểm cao nhất trong khoảng period
    # Tìm swing low: điểm thấp nhất trong khoảng period
```

#### 2. Phát Hiện Break of Structure (BOS)
```python
def detect_break_of_structure(df, min_move_percentage=2.0):
    # Bullish BOS: Giá vượt qua swing high gần nhất ≥2%
    # Bearish BOS: Giá phá vỡ swing low gần nhất ≥2%
```

#### 3. Xác Định Order Block
```python
def detect_order_blocks(df, lookback_period=20):
    # Bullish OB: Nến giảm cuối cùng trước BOS tăng
    # Bearish OB: Nến tăng cuối cùng trước BOS giảm
    # Điều kiện: Phải có chuyển động ≥1.5%
```

### Tiêu Chí Phát Hiện

- **Bullish Order Block**: Nến đỏ cuối cùng trước một đợt tăng mạnh phá vỡ cấu trúc
- **Bearish Order Block**: Nến xanh cuối cùng trước một đợt giảm mạnh phá vỡ cấu trúc
- **Ngưỡng chuyển động tối thiểu**: 1.5% để xác nhận
- **Ngưỡng BOS**: 2.0% để xác nhận phá vỡ cấu trúc

## 🛠️ Khắc Phục Sự Cố

### Lỗi Thường Gặp

#### 1. "Failed to fetch data"
**Nguyên nhân**: Không kết nối được API Binance
**Giải pháp**:
```bash
# Kiểm tra kết nối internet
ping google.com

# Thử cặp coin khác
# Khởi động lại ứng dụng
```

#### 2. "Module not found"
**Nguyên nhân**: Thiếu thư viện Python
**Giải pháp**:
```bash
# Cài đặt lại requirements
pip install -r requirements.txt

# Hoặc cài từng thư viện
pip install Flask flask-cors ccxt pandas numpy plotly
```

#### 3. "Port already in use"
**Nguyên nhân**: Port 5000 đã được sử dụng
**Giải pháp**:
```bash
# Tìm process đang dùng port 5000
netstat -ano | findstr :5000

# Kill process (Windows)
taskkill /PID [PID_NUMBER] /F

# Hoặc đổi port trong app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

#### 4. Biểu đồ không hiển thị
**Nguyên nhân**: JavaScript bị chặn hoặc lỗi
**Giải pháp**:
- Bật JavaScript trong trình duyệt
- Tắt AdBlock
- Thử trình duyệt khác
- Kiểm tra Console (F12)

#### 5. Không thể truy cập từ máy khác
**Nguyên nhân**: Firewall hoặc cấu hình mạng
**Giải pháp**:
```bash
# Kiểm tra firewall
# Windows: Tắt Windows Firewall tạm thời để test
# Linux: sudo ufw allow 5000

# Kiểm tra IP và port
netstat -an | findstr :5000

# Kiểm tra từ máy khác
ping [IP-may-chu]
telnet [IP-may-chu] 5000
```

### Kiểm Tra Logs

```bash
# Trong terminal đang chạy app
# Xem thông báo lỗi và debug info
```

## ❓ Câu Hỏi Thường Gặp

### Q: Ứng dụng có miễn phí không?
**A**: Hoàn toàn miễn phí. Chỉ cần kết nối internet để lấy dữ liệu từ Binance.

### Q: Tôi có thể thêm sàn giao dịch khác không?
**A**: Có, bạn có thể chỉnh sửa code để thêm Bybit, KuCoin, v.v. thông qua thư viện CCXT.

### Q: Order Block có chính xác 100% không?
**A**: Không. Đây là công cụ hỗ trợ phân tích, không phải lời khuyên đầu tư. Luôn kết hợp với phân tích khác.

### Q: Làm sao để thay đổi thông số phát hiện?
**A**: Chỉnh sửa các tham số trong file `app.py`:
- `min_move_percentage`: Ngưỡng BOS (mặc định 2.0%)
- `lookback_period`: Số nến nhìn lại (mặc định 20)
- Ngưỡng Order Block: 1.5%

### Q: Ứng dụng có hoạt động 24/7 không?
**A**: Khi deploy lên hosting (Heroku, Railway, Render), ứng dụng sẽ chạy 24/7.

### Q: Tôi có thể tùy chỉnh giao diện không?
**A**: Có, chỉnh sửa file `templates/index.html` và CSS để thay đổi giao diện.

### Q: Làm sao truy cập từ IP tĩnh?
**A**: 
1. Tìm IP của máy chủ: `ipconfig` (Windows) hoặc `ifconfig` (Mac/Linux)
2. Truy cập từ máy khác: `http://[IP-may-chu]:5000`
3. Đảm bảo firewall cho phép port 5000
4. Cấu hình port forwarding trên router nếu muốn truy cập từ internet

### Q: Port 5000 bị chặn, làm sao đổi port?
**A**: Chỉnh sửa file `app.py`, dòng cuối:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Đổi 5000 thành port khác
```

## 📞 Hỗ Trợ và Liên Hệ

### Báo Lỗi
- Kiểm tra Console trình duyệt (F12)
- Ghi lại thông báo lỗi cụ thể
- Mô tả các bước tái hiện lỗi

### Đóng Góp
- Fork repository
- Tạo branch mới cho feature
- Submit pull request

### Tài Liệu Tham Khảo
- [Flask Documentation](https://flask.palletsprojects.com/)
- [CCXT Library](https://github.com/ccxt/ccxt)
- [Plotly Python](https://plotly.com/python/)
- [Smart Money Concepts](https://www.tradingview.com/ideas/smartmoney/)

## ⚠️ Tuyên Bố Miễn Trừ Trách Nhiệm

1. **Mục đích giáo dục**: Công cụ này chỉ dành cho học tập và phân tích
2. **Không phải lời khuyên tài chính**: Giao dịch có rủi ro cao
3. **Tự chịu trách nhiệm**: Luôn nghiên cứu kỹ trước khi đầu tư
4. **Không đảm bảo**: Kết quả có thể sai lệch trong một số điều kiện thị trường

---

## 🎉 Kết Luận

Ứng dụng **Crypto Order Block Detector** là công cụ mạnh mẽ giúp bạn:
- ✅ Phân tích thị trường cryptocurrency chuyên nghiệp
- ✅ Hiểu rõ về Smart Money Concepts
- ✅ Phát hiện Order Block và BOS tự động
- ✅ Có giao diện đẹp mắt và dễ sử dụng
- ✅ Deploy lên hosting miễn phí
- ✅ Truy cập từ bất kỳ đâu trong mạng với IP tĩnh

**Chúc bạn trading thành công! 📈💰**

*Nhớ rằng: Đây chỉ là công cụ phân tích. Hãy luôn tự nghiên cứu và không bao giờ rủi ro nhiều hơn mức bạn có thể chịu đựng được.*   