# 🚀 HƯỚNG DẪN NHANH - Ứng Dụng Phát Hiện Order Block

## ⚡ Bắt Đầu Trong 5 Phút

### Bước 1: Chuẩn Bị
1. **Tải Python** từ [python.org](https://python.org) (phiên bản 3.11+)
2. **Tải tất cả files** về máy tính

### Bước 2: Chạy Ứng Dụng
**Windows**: Double-click file `start.bat`
**Mac/Linux**: Mở Terminal và chạy:
```bash
pip install -r requirements.txt
python app.py
```

### Bước 3: Sử Dụng
1. Mở trình duyệt → `http://localhost:5000`
2. Chọn cặp coin (VD: BTC/USDT)
3. Chọn khung thời gian (VD: 1h)
4. Click **"Analyze Order Blocks"**

## 🌐 Truy Cập Qua IP Tĩnh

### Tìm IP Máy Chủ
```bash
# Windows
ipconfig

# Mac/Linux  
ifconfig
```

### Truy Cập Từ Máy Khác
```
http://192.168.1.100:5000
# (Thay 192.168.1.100 bằng IP thực của máy chủ)
```

### Mở Firewall (Nếu Cần)
**Windows**: `netsh advfirewall firewall add rule name="Flask" dir=in action=allow protocol=TCP localport=5000`
**Linux**: `sudo ufw allow 5000`

## 📊 Đọc Hiểu Kết Quả

| Màu sắc | Ý nghĩa |
|---------|---------|
| 🟢 Hình chữ nhật xanh | Vùng mua (Bullish Order Block) |
| 🔴 Hình chữ nhật đỏ | Vùng bán (Bearish Order Block) |
| 🔺 Tam giác xanh | Phá vỡ cấu trúc tăng |
| 🔻 Tam giác đỏ | Phá vỡ cấu trúc giảm |

## 🌐 Deploy Lên Internet (Miễn Phí)

### Heroku (Đơn giản nhất)
```bash
# 1. Tạo tài khoản tại heroku.com
# 2. Cài Heroku CLI
# 3. Chạy lệnh:
heroku login
heroku create ten-app-cua-ban
git init
git add .
git commit -m "Deploy app"
git push heroku main
```

### Railway (Nhanh nhất)
1. Đi tới [railway.app](https://railway.app)
2. Đăng nhập bằng GitHub
3. "New Project" → "Deploy from GitHub"
4. Chọn repository → Tự động deploy

## 🛠️ Khắc Phục Lỗi Nhanh

| Lỗi | Giải pháp |
|-----|-----------|
| "Module not found" | Chạy `pip install -r requirements.txt` |
| "Port in use" | Đổi port trong app.py từ 5000 → 5001 |
| "Failed to fetch data" | Kiểm tra internet, thử cặp coin khác |
| Biểu đồ không hiện | Bật JavaScript, tắt AdBlock |
| Không truy cập được từ máy khác | Kiểm tra firewall, IP, ping test |

## 💡 Tips Sử Dụng

- **Scalping**: Dùng khung 15m
- **Day Trading**: Dùng khung 1h
- **Swing Trading**: Dùng khung 4h
- **Đầu tư dài hạn**: Dùng khung 1d

## ⚠️ Lưu Ý Quan Trọng

❌ **KHÔNG** sử dụng làm lời khuyên đầu tư  
❌ **KHÔNG** tin tưởng 100% vào kết quả  
✅ **CÓ** kết hợp với phân tích khác  
✅ **CÓ** quản lý rủi ro tốt  

## 🆘 Cần Hỗ Trợ?

- Đọc file `HUONG_DAN_TIENG_VIET.md` để biết chi tiết
- Kiểm tra Console trình duyệt (F12) nếu có lỗi
- Chạy lệnh `python deploy.py` để có menu deploy tự động

---

**Happy Trading! 🎯📈** 