#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Cài Đặt Tự Động - Ứng Dụng Phát Hiện Order Block Cryptocurrency
Phiên bản Tiếng Việt
"""

import os
import subprocess
import sys
import platform


def chay_lenh(lenh, bat_output=True):
    """Chạy lệnh shell và trả về kết quả"""
    try:
        if bat_output:
            ket_qua = subprocess.run(
                lenh, shell=True, capture_output=True, text=True, encoding='utf-8')
            return ket_qua.returncode == 0, ket_qua.stdout, ket_qua.stderr
        else:
            ket_qua = subprocess.run(lenh, shell=True)
            return ket_qua.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)


def kiem_tra_python():
    """Kiểm tra Python có được cài đặt không"""
    print("🔍 Đang kiểm tra Python...")

    thanh_cong, stdout, stderr = chay_lenh("python --version")
    if thanh_cong:
        phien_ban = stdout.strip()
        print(f"✅ Python đã cài đặt: {phien_ban}")

        # Kiểm tra phiên bản
        if "3.11" in phien_ban or "3.12" in phien_ban:
            print("✅ Phiên bản Python phù hợp")
            return True
        else:
            print("⚠️ Phiên bản Python cũ, khuyến nghị 3.11+")
            return True
    else:
        print("❌ Python chưa được cài đặt")
        print("📥 Vui lòng tải Python từ: https://python.org")
        return False


def kiem_tra_pip():
    """Kiểm tra pip có hoạt động không"""
    print("\n🔍 Đang kiểm tra pip...")

    thanh_cong, stdout, stderr = chay_lenh("pip --version")
    if thanh_cong:
        print(f"✅ pip hoạt động tốt: {stdout.strip()}")
        return True
    else:
        print("❌ pip không hoạt động")
        return False


def cai_dat_thu_vien():
    """Cài đặt các thư viện cần thiết"""
    print("\n📦 Đang cài đặt thư viện Python...")
    print("⏳ Quá trình này có thể mất 2-3 phút...")

    # Upgrade pip trước
    print("🔄 Đang nâng cấp pip...")
    chay_lenh("python -m pip install --upgrade pip")

    # Cài đặt requirements
    thanh_cong, stdout, stderr = chay_lenh("pip install -r requirements.txt")

    if thanh_cong:
        print("✅ Cài đặt thư viện thành công!")
        return True
    else:
        print("❌ Lỗi cài đặt thư viện:")
        print(stderr)

        # Thử cài đặt từng thư viện riêng lẻ
        print("\n🔄 Đang thử cài đặt từng thư viện...")
        thu_vien = [
            "Flask", "flask-cors", "ccxt", "pandas",
            "numpy", "plotly", "gunicorn", "python-dotenv",
            "requests", "websocket-client"
        ]

        for lib in thu_vien:
            print(f"📦 Cài đặt {lib}...")
            thanh_cong, _, _ = chay_lenh(f"pip install {lib}")
            if thanh_cong:
                print(f"✅ {lib} - OK")
            else:
                print(f"❌ {lib} - Lỗi")

        return True


def tao_virtual_env():
    """Tạo virtual environment"""
    print("\n🏗️ Tạo môi trường ảo Python...")

    if os.path.exists('venv'):
        print("✅ Virtual environment đã tồn tại")
        return True

    thanh_cong, stdout, stderr = chay_lenh("python -m venv venv")
    if thanh_cong:
        print("✅ Tạo virtual environment thành công")
        return True
    else:
        print("❌ Không thể tạo virtual environment")
        print("🔄 Tiếp tục cài đặt global...")
        return False


def kich_hoat_venv():
    """Kích hoạt virtual environment"""
    he_thong = platform.system()

    if he_thong == "Windows":
        lenh_kich_hoat = "venv\\Scripts\\activate"
    else:
        lenh_kich_hoat = "source venv/bin/activate"

    print(f"💡 Để kích hoạt virtual environment sau này:")
    print(f"   {lenh_kich_hoat}")


def chay_ung_dung():
    """Chạy ứng dụng"""
    print("\n🚀 Khởi động ứng dụng...")
    print("🌐 Ứng dụng sẽ chạy tại: http://localhost:5000")
    print("⏹️ Nhấn Ctrl+C để dừng server")
    print("=" * 50)

    try:
        chay_lenh("python app.py", bat_output=False)
    except KeyboardInterrupt:
        print("\n👋 Đã dừng ứng dụng")


def tao_shortcut():
    """Tạo shortcut để chạy nhanh"""
    print("\n📋 Tạo file khởi động nhanh...")

    he_thong = platform.system()

    if he_thong == "Windows":
        noi_dung = """@echo off
echo 🚀 Khởi động Crypto Order Block Detector...
echo ========================================

cd /d "%~dp0"

if exist venv (
    call venv\\Scripts\\activate
    echo ✅ Đã kích hoạt virtual environment
)

echo 🌐 Mở trình duyệt và vào: http://localhost:5000
echo ⏹️ Nhấn Ctrl+C để dừng server
echo ========================================

python app.py

pause
"""
        with open('khoi_dong.bat', 'w', encoding='utf-8') as f:
            f.write(noi_dung)
        print("✅ Đã tạo file 'khoi_dong.bat'")
        print("💡 Lần sau chỉ cần double-click 'khoi_dong.bat' để chạy")

    else:
        noi_dung = """#!/bin/bash
echo "🚀 Khởi động Crypto Order Block Detector..."
echo "========================================"

cd "$(dirname "$0")"

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Đã kích hoạt virtual environment"
fi

echo "🌐 Mở trình duyệt và vào: http://localhost:5000"
echo "⏹️ Nhấn Ctrl+C để dừng server"
echo "========================================"

python app.py
"""
        with open('khoi_dong.sh', 'w', encoding='utf-8') as f:
            f.write(noi_dung)

        # Cấp quyền thực thi
        os.chmod('khoi_dong.sh', 0o755)
        print("✅ Đã tạo file 'khoi_dong.sh'")
        print("💡 Lần sau chạy: ./khoi_dong.sh")


def hien_thi_huong_dan():
    """Hiển thị hướng dẫn sử dụng"""
    print("\n" + "="*60)
    print("🎉 CÀI ĐẶT HOÀN TẤT!")
    print("="*60)
    print("📖 HƯỚNG DẪN SỬ DỤNG:")
    print("1. Mở trình duyệt web")
    print("2. Vào địa chỉ: http://localhost:5000")
    print("3. Chọn cặp coin (VD: BTC/USDT)")
    print("4. Chọn khung thời gian (VD: 1h)")
    print("5. Click 'Analyze Order Blocks'")
    print("\n🔍 GIẢI THÍCH KẾT QUẢ:")
    print("🟢 Hình chữ nhật xanh = Bullish Order Block (vùng mua)")
    print("🔴 Hình chữ nhật đỏ = Bearish Order Block (vùng bán)")
    print("🔺 Tam giác xanh = Bullish BOS (phá vỡ cấu trúc tăng)")
    print("🔻 Tam giác đỏ = Bearish BOS (phá vỡ cấu trúc giảm)")
    print("\n📚 TÀI LIỆU THAM KHẢO:")
    print("- HUONG_DAN_TIENG_VIET.md (hướng dẫn chi tiết)")
    print("- HUONG_DAN_NHANH.md (hướng dẫn nhanh)")
    print("- README.md (tiếng Anh)")
    print("\n⚠️ LƯU Ý:")
    print("❌ Đây KHÔNG phải lời khuyên đầu tư")
    print("❌ Luôn quản lý rủi ro và nghiên cứu kỹ")
    print("✅ Chỉ dùng làm công cụ hỗ trợ phân tích")


def main():
    """Hàm chính"""
    print("🚀 SCRIPT CÀI ĐẶT TỰ ĐỘNG")
    print("Ứng Dụng Phát Hiện Order Block Cryptocurrency")
    print("=" * 60)

    # Kiểm tra Python
    if not kiem_tra_python():
        print("\n❌ Vui lòng cài đặt Python trước khi tiếp tục")
        input("Nhấn Enter để thoát...")
        return

    # Kiểm tra pip
    if not kiem_tra_pip():
        print("\n❌ pip không hoạt động, vui lòng kiểm tra cài đặt Python")
        input("Nhấn Enter để thoát...")
        return

    # Tạo virtual environment (tùy chọn)
    while True:
        lua_chon = input(
            "\n❓ Bạn có muốn tạo virtual environment? (khuyến nghị) [y/n]: ").lower()
        if lua_chon in ['y', 'yes', 'có', '']:
            if tao_virtual_env():
                kich_hoat_venv()
            break
        elif lua_chon in ['n', 'no', 'không']:
            print("⏭️ Bỏ qua tạo virtual environment")
            break
        else:
            print("❓ Vui lòng nhập 'y' hoặc 'n'")

    # Cài đặt thư viện
    if not cai_dat_thu_vien():
        print("\n❌ Cài đặt thư viện thất bại")
        input("Nhấn Enter để thoát...")
        return

    # Tạo shortcut
    tao_shortcut()

    # Hiển thị hướng dẫn
    hien_thi_huong_dan()

    # Hỏi có chạy ứng dụng ngay không
    while True:
        lua_chon = input(
            "\n❓ Bạn có muốn chạy ứng dụng ngay bây giờ? [y/n]: ").lower()
        if lua_chon in ['y', 'yes', 'có', '']:
            chay_ung_dung()
            break
        elif lua_chon in ['n', 'no', 'không']:
            print("👋 Cài đặt hoàn tất! Chạy 'python app.py' để khởi động")
            break
        else:
            print("❓ Vui lòng nhập 'y' hoặc 'n'")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Đã hủy cài đặt")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        input("Nhấn Enter để thoát...")
