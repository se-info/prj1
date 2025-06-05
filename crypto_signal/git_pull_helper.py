#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Pull Helper - Script Python để pull code từ remote repository
Dành cho: https://github.com/se-info/prj1.git
"""

import subprocess
import os


def chay_lenh(lenh):
    """Chạy lệnh và hiển thị kết quả"""
    print(f"🔄 Đang chạy: {lenh}")
    try:
        ket_qua = subprocess.run(
            lenh, shell=True, capture_output=True,
            text=True, encoding='utf-8'
        )

        if ket_qua.returncode == 0:
            print("✅ Thành công!")
            if ket_qua.stdout.strip():
                print(f"📄 Output:\n{ket_qua.stdout.strip()}")
            return True
        else:
            print("❌ Lỗi!")
            if ket_qua.stderr.strip():
                print(f"🚨 Error:\n{ket_qua.stderr.strip()}")
            return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False


def main():
    """Script chính để pull từ Git"""
    print("🚀 GIT PULL HELPER")
    print("="*50)
    print("Repository: https://github.com/se-info/prj1.git")
    print("="*50)

    # Bước 1: Kiểm tra Git có sẵn không
    print("\n1️⃣ Kiểm tra Git...")
    if not chay_lenh("git --version"):
        print("❌ Git chưa được cài đặt!")
        print("📥 Tải Git tại: https://git-scm.com/download")
        return

    # Bước 2: Kiểm tra có phải Git repository không
    print("\n2️⃣ Kiểm tra Git repository...")
    if not os.path.exists('.git'):
        print("⚠️ Chưa khởi tạo Git repository")

        # Khởi tạo Git repo
        print("🏗️ Khởi tạo Git repository...")
        if not chay_lenh("git init"):
            return
    else:
        print("✅ Git repository đã tồn tại")

    # Bước 3: Thêm remote origin
    print("\n3️⃣ Cấu hình remote origin...")
    repo_url = "https://github.com/se-info/prj1.git"

    # Kiểm tra remote hiện tại
    print("🔍 Kiểm tra remote hiện tại...")
    ket_qua = subprocess.run(
        "git remote -v", shell=True, capture_output=True, text=True
    )

    if "origin" in ket_qua.stdout:
        print("⚠️ Remote origin đã tồn tại:")
        print(ket_qua.stdout.strip())

        # Cập nhật URL
        print(f"🔄 Cập nhật remote origin: {repo_url}")
        chay_lenh(f"git remote set-url origin {repo_url}")
    else:
        # Thêm remote mới
        print(f"➕ Thêm remote origin: {repo_url}")
        chay_lenh(f"git remote add origin {repo_url}")

    # Bước 4: Fetch từ remote
    print("\n4️⃣ Fetch updates từ remote...")
    if not chay_lenh("git fetch origin"):
        print("❌ Không thể fetch từ remote")
        print("💡 Kiểm tra kết nối internet và URL repository")
        return

    # Bước 5: Pull từ remote
    print("\n5️⃣ Pull code từ remote...")

    # Kiểm tra branch hiện tại
    ket_qua = subprocess.run(
        "git branch --show-current", shell=True,
        capture_output=True, text=True
    )

    current_branch = ket_qua.stdout.strip()
    if current_branch:
        print(f"📍 Branch hiện tại: {current_branch}")
        target_branch = current_branch
    else:
        print("📍 Chưa có branch, sẽ tạo main branch")
        target_branch = "main"

    # Thực hiện pull
    pull_command = f"git pull origin {target_branch}"
    print(f"⬇️ Pull từ origin/{target_branch}...")

    if chay_lenh(pull_command):
        print("\n🎉 PULL THÀNH CÔNG!")
        print("✅ Code đã được cập nhật từ remote repository")
    else:
        print("\n🔧 TROUBLESHOOTING:")
        print("1. Kiểm tra kết nối internet")
        print("2. Đảm bảo URL repository đúng")
        print("3. Kiểm tra quyền truy cập repository")

        # Gợi ý thử pull main branch
        if target_branch != "main":
            print(f"\n💡 Thử pull từ main branch:")
            print("git pull origin main")

            lua_chon = input("Bạn có muốn thử pull từ main? [y/n]: ").lower()
            if lua_chon in ['y', 'yes']:
                chay_lenh("git pull origin main")

    # Bước 6: Hiển thị trạng thái
    print("\n6️⃣ Trạng thái hiện tại:")
    print("📊 Git status:")
    chay_lenh("git status --short")

    print("\n📜 Commit gần nhất:")
    chay_lenh("git log --oneline -3")

    print("\n" + "="*50)
    print("🎯 WORKFLOW TIẾP THEO:")
    print("="*50)
    print("1. 📝 Chỉnh sửa code")
    print("2. 📦 git add .")
    print("3. 💬 git commit -m 'Your message'")
    print("4. 📤 git push origin main")
    print("="*50)


if __name__ == "__main__":
    try:
        main()
        input("\nNhấn Enter để thoát...")
    except KeyboardInterrupt:
        print("\n\n👋 Đã hủy")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        input("Nhấn Enter để thoát...")
