#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script Kiểm Tra IP - Ứng Dụng Phát Hiện Order Block
Hiển thị IP để truy cập từ các máy khác trong mạng
"""

import socket
import subprocess
import platform
import sys


def lay_ip_local():
    """Lấy IP address của máy trong mạng LAN"""
    try:
        # Tạo socket và kết nối đến một địa chỉ bên ngoài
        # Không thực sự gửi data, chỉ để lấy IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def lay_ip_bang_lenh():
    """Lấy IP bằng lệnh hệ thống"""
    he_thong = platform.system()

    try:
        if he_thong == "Windows":
            # Chạy ipconfig và tìm IPv4
            ket_qua = subprocess.run(
                ["ipconfig"],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )

            lines = ket_qua.stdout.split('\n')
            for line in lines:
                if 'IPv4 Address' in line or 'IPv4' in line:
                    if '192.168.' in line or '10.' in line or '172.' in line:
                        ip = line.split(':')[-1].strip()
                        if ip and ip != '127.0.0.1':
                            return ip

        elif he_thong in ["Linux", "Darwin"]:  # Darwin = macOS
            # Chạy ifconfig
            ket_qua = subprocess.run(
                ["ifconfig"],
                capture_output=True,
                text=True
            )

            lines = ket_qua.stdout.split('\n')
            for line in lines:
                if 'inet ' in line and 'inet addr:' not in line:
                    parts = line.split()
                    for part in parts:
                        if part.startswith('192.168.') or part.startswith('10.') or part.startswith('172.'):
                            return part

    except Exception as e:
        print(f"Lỗi khi chạy lệnh: {e}")

    return None


def kiem_tra_port_mo(ip, port=5000):
    """Kiểm tra xem port có đang mở không"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        ket_qua = sock.connect_ex((ip, port))
        sock.close()
        return ket_qua == 0
    except Exception:
        return False


def hien_thi_thong_tin():
    """Hiển thị thông tin IP và hướng dẫn"""
    print("🔍 KIỂM TRA IP VÀ KHAI BÁO TRUY CẬP")
    print("=" * 50)

    # Lấy IP bằng nhiều cách
    ip_socket = lay_ip_local()
    ip_lenh = lay_ip_bang_lenh()

    print(f"🖥️  Hệ thống: {platform.system()}")
    print(f"💻 Tên máy: {socket.gethostname()}")

    # Hiển thị các IP tìm được
    danh_sach_ip = []

    if ip_socket:
        danh_sach_ip.append(ip_socket)
        print(f"🌐 IP (Socket): {ip_socket}")

    if ip_lenh and ip_lenh != ip_socket:
        danh_sach_ip.append(ip_lenh)
        print(f"🌐 IP (Command): {ip_lenh}")

    if not danh_sach_ip:
        print("❌ Không tìm thấy IP trong mạng LAN")
        print("💡 Thử chạy lệnh thủ công:")
        if platform.system() == "Windows":
            print("   ipconfig")
        else:
            print("   ifconfig")
        return

    # Lấy IP chính (ưu tiên socket)
    ip_chinh = ip_socket if ip_socket else ip_lenh

    print("\n" + "="*50)
    print("📱 TRUY CẬP TỪ CÁC MÁY KHÁC:")
    print("="*50)

    for ip in set(danh_sach_ip):  # Loại bỏ trùng lặp
        url = f"http://{ip}:5000"
        print(f"🔗 {url}")

        # Kiểm tra port có mở không
        port_mo = kiem_tra_port_mo(ip)
        if port_mo:
            print(f"   ✅ Port 5000 đang mở")
        else:
            print(f"   ⚠️ Port 5000 chưa mở (ứng dụng chưa chạy?)")

    print("\n" + "="*50)
    print("📋 HƯỚNG DẪN SỬ DỤNG:")
    print("="*50)
    print("1. 🚀 Chạy ứng dụng: python app.py")
    print("2. 📱 Từ máy khác, vào một trong các URL trên")
    print("3. 🔥 Nếu không truy cập được, kiểm tra firewall:")

    if platform.system() == "Windows":
        print("   Windows: Chạy PowerShell với quyền Admin:")
        print("   netsh advfirewall firewall add rule name=\"Flask\" dir=in action=allow protocol=TCP localport=5000")
    else:
        print("   Linux/macOS:")
        print("   sudo ufw allow 5000")

    print("\n💡 KIỂM TRA KẾT NỐI:")
    print("Từ máy khác, chạy:")
    print(f"ping {ip_chinh}")
    print(f"telnet {ip_chinh} 5000")

    print("\n⚠️ LƯU Ý:")
    print("- Tất cả máy phải cùng mạng WiFi/LAN")
    print("- Firewall có thể chặn kết nối")
    print("- Router có thể có cài đặt chặn AP isolation")


def main():
    """Hàm chính"""
    try:
        hien_thi_thong_tin()
        input("\nNhấn Enter để thoát...")
    except KeyboardInterrupt:
        print("\n\n👋 Đã hủy")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        input("Nhấn Enter để thoát...")


if __name__ == "__main__":
    main()
