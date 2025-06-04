#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git Helper Script - Hướng dẫn và tự động hóa Git workflow
Dành cho dự án Crypto Order Block Detector
"""

import os
import subprocess
import sys
from pathlib import Path


def chay_lenh_git(lenh, check_output=True):
    """Chạy lệnh git và trả về kết quả"""
    try:
        if check_output:
            ket_qua = subprocess.run(
                lenh, shell=True, capture_output=True,
                text=True, encoding='utf-8'
            )
            return ket_qua.returncode == 0, ket_qua.stdout.strip(), ket_qua.stderr.strip()
        else:
            ket_qua = subprocess.run(lenh, shell=True)
            return ket_qua.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)


def kiem_tra_git():
    """Kiểm tra Git có được cài đặt không"""
    print("🔍 Kiểm tra Git...")
    thanh_cong, stdout, stderr = chay_lenh_git("git --version")

    if thanh_cong:
        print(f"✅ {stdout}")
        return True
    else:
        print("❌ Git chưa được cài đặt")
        print("📥 Tải Git tại: https://git-scm.com/download")
        return False


def kiem_tra_git_repo():
    """Kiểm tra thư mục hiện tại có phải Git repository không"""
    return os.path.exists('.git')


def khoi_tao_git_repo():
    """Khởi tạo Git repository"""
    print("\n🏗️ Khởi tạo Git repository...")

    if kiem_tra_git_repo():
        print("✅ Git repository đã tồn tại")
        return True

    thanh_cong, stdout, stderr = chay_lenh_git("git init")

    if thanh_cong:
        print("✅ Đã khởi tạo Git repository")
        return True
    else:
        print(f"❌ Lỗi khởi tạo: {stderr}")
        return False


def them_remote_origin(url_repo):
    """Thêm remote origin"""
    print(f"\n🔗 Thêm remote origin: {url_repo}")

    # Kiểm tra origin đã tồn tại chưa
    thanh_cong, stdout, stderr = chay_lenh_git("git remote -v")

    if "origin" in stdout:
        print("⚠️ Remote origin đã tồn tại:")
        print(stdout)

        # Hỏi có muốn thay đổi không
        lua_chon = input("Bạn có muốn thay đổi URL origin? [y/n]: ").lower()
        if lua_chon in ['y', 'yes', 'có']:
            thanh_cong, _, stderr = chay_lenh_git(
                f"git remote set-url origin {url_repo}")
            if thanh_cong:
                print("✅ Đã cập nhật remote origin")
                return True
            else:
                print(f"❌ Lỗi cập nhật: {stderr}")
                return False
        else:
            return True
    else:
        # Thêm origin mới
        thanh_cong, stdout, stderr = chay_lenh_git(
            f"git remote add origin {url_repo}")

        if thanh_cong:
            print("✅ Đã thêm remote origin")
            return True
        else:
            print(f"❌ Lỗi thêm remote: {stderr}")
            return False


def pull_tu_remote(branch="main"):
    """Pull code từ remote repository"""
    print(f"\n📥 Pull code từ remote (branch: {branch})...")

    # Kiểm tra branch hiện tại
    thanh_cong, current_branch, _ = chay_lenh_git("git branch --show-current")

    if current_branch:
        print(f"📍 Branch hiện tại: {current_branch}")

    # Fetch trước để cập nhật thông tin remote
    print("🔄 Fetch updates từ remote...")
    thanh_cong, stdout, stderr = chay_lenh_git("git fetch origin")

    if not thanh_cong:
        print(f"❌ Lỗi fetch: {stderr}")
        return False

    # Pull code
    lenh_pull = f"git pull origin {branch}"
    print(f"⬇️ Đang pull: {lenh_pull}")

    thanh_cong, stdout, stderr = chay_lenh_git(lenh_pull)

    if thanh_cong:
        print("✅ Pull thành công!")
        if stdout:
            print(f"📄 Kết quả:\n{stdout}")
        return True
    else:
        print(f"❌ Lỗi pull: {stderr}")

        # Gợi ý xử lý conflict
        if "merge conflict" in stderr.lower() or "conflict" in stderr.lower():
            print("\n🔧 PHÁT HIỆN CONFLICT:")
            print("1. Xử lý conflict trong các file bị đánh dấu")
            print("2. Chạy: git add .")
            print("3. Chạy: git commit -m 'Resolve conflicts'")
            print("4. Thử pull lại")

        return False


def push_len_remote(branch="main"):
    """Push code lên remote repository"""
    print(f"\n📤 Push code lên remote (branch: {branch})...")

    # Kiểm tra có thay đổi cần commit không
    thanh_cong, status, _ = chay_lenh_git("git status --porcelain")

    if status.strip():
        print("📝 Có thay đổi chưa commit:")
        print(status)

        lua_chon = input("Bạn có muốn commit tất cả thay đổi? [y/n]: ").lower()
        if lua_chon in ['y', 'yes', 'có']:
            commit_message = input(
                "Nhập commit message: ") or "Update project files"

            # Add và commit
            chay_lenh_git("git add .")
            thanh_cong, _, stderr = chay_lenh_git(
                f'git commit -m "{commit_message}"')

            if not thanh_cong and "nothing to commit" not in stderr:
                print(f"❌ Lỗi commit: {stderr}")
                return False

    # Push lên remote
    lenh_push = f"git push origin {branch}"
    print(f"⬆️ Đang push: {lenh_push}")

    thanh_cong, stdout, stderr = chay_lenh_git(lenh_push, check_output=False)

    if thanh_cong:
        print("✅ Push thành công!")
        return True
    else:
        print(f"❌ Lỗi push: {stderr}")
        return False


def clone_repository(url_repo, thu_muc=None):
    """Clone repository từ remote"""
    print(f"\n📥 Clone repository: {url_repo}")

    if thu_muc:
        lenh_clone = f"git clone {url_repo} {thu_muc}"
    else:
        lenh_clone = f"git clone {url_repo}"

    print(f"⬇️ Đang clone: {lenh_clone}")
    thanh_cong, stdout, stderr = chay_lenh_git(lenh_clone, check_output=False)

    if thanh_cong:
        print("✅ Clone thành công!")
        return True
    else:
        print(f"❌ Lỗi clone: {stderr}")
        return False


def hien_thi_menu():
    """Hiển thị menu chính"""
    print("\n" + "="*60)
    print("🚀 GIT HELPER - CRYPTO ORDER BLOCK DETECTOR")
    print("="*60)
    print("1. 🏗️  Khởi tạo Git repository")
    print("2. 🔗 Thêm remote origin")
    print("3. 📥 Pull từ remote")
    print("4. 📤 Push lên remote")
    print("5. 📋 Clone repository")
    print("6. 📊 Xem trạng thái Git")
    print("7. 📜 Xem lịch sử commit")
    print("8. 🌿 Quản lý branch")
    print("9. ❓ Hướng dẫn Git workflow")
    print("0. 🚪 Thoát")
    print("="*60)


def xem_trang_thai_git():
    """Xem trạng thái Git hiện tại"""
    print("\n📊 TRẠNG THÁI GIT:")
    print("="*40)

    # Branch hiện tại
    thanh_cong, branch, _ = chay_lenh_git("git branch --show-current")
    if thanh_cong and branch:
        print(f"🌿 Branch hiện tại: {branch}")

    # Remote repositories
    thanh_cong, remotes, _ = chay_lenh_git("git remote -v")
    if thanh_cong and remotes:
        print(f"🔗 Remote repositories:\n{remotes}")

    # Trạng thái file
    thanh_cong, status, _ = chay_lenh_git("git status --short")
    if thanh_cong:
        if status:
            print(f"📝 Thay đổi:\n{status}")
        else:
            print("✅ Working directory clean")


def xem_lich_su_commit():
    """Xem lịch sử commit"""
    print("\n📜 LỊCH SỬ COMMIT (10 gần nhất):")
    print("="*50)

    lenh = "git log --oneline --graph -10"
    thanh_cong, stdout, _ = chay_lenh_git(lenh)

    if thanh_cong and stdout:
        print(stdout)
    else:
        print("❌ Không có commit nào hoặc chưa khởi tạo Git")


def quan_ly_branch():
    """Quản lý branch"""
    print("\n🌿 QUẢN LÝ BRANCH:")
    print("="*30)

    # Hiển thị các branch
    thanh_cong, branches, _ = chay_lenh_git("git branch -a")
    if thanh_cong and branches:
        print("📋 Các branch:")
        print(branches)

    print("\n1. Tạo branch mới")
    print("2. Chuyển branch")
    print("3. Quay lại menu chính")

    lua_chon = input("Chọn tùy chọn [1-3]: ").strip()

    if lua_chon == "1":
        ten_branch = input("Nhập tên branch mới: ").strip()
        if ten_branch:
            thanh_cong, _, stderr = chay_lenh_git(
                f"git checkout -b {ten_branch}")
            if thanh_cong:
                print(f"✅ Đã tạo và chuyển đến branch: {ten_branch}")
            else:
                print(f"❌ Lỗi: {stderr}")

    elif lua_chon == "2":
        ten_branch = input("Nhập tên branch muốn chuyển: ").strip()
        if ten_branch:
            thanh_cong, _, stderr = chay_lenh_git(f"git checkout {ten_branch}")
            if thanh_cong:
                print(f"✅ Đã chuyển đến branch: {ten_branch}")
            else:
                print(f"❌ Lỗi: {stderr}")


def huong_dan_git_workflow():
    """Hiển thị hướng dẫn Git workflow"""
    print("\n" + "="*60)
    print("📚 HƯỚNG DẪN GIT WORKFLOW")
    print("="*60)
    print("""
🔄 WORKFLOW CƠ BẢN:

1. 🏗️  KHỞI TẠO DỰ ÁN:
   git init
   git remote add origin https://github.com/se-info/prj1.git

2. 📥 PULL CODE TỪ REMOTE (LẦN ĐẦU):
   git pull origin main
   # hoặc
   git clone https://github.com/se-info/prj1.git

3. 🔄 WORKFLOW HÀNG NGÀY:
   git pull origin main          # Pull code mới nhất
   # ... làm việc với code ...
   git add .                     # Add thay đổi
   git commit -m "Your message"  # Commit thay đổi
   git push origin main          # Push lên remote

4. 🌿 WORKING WITH BRANCHES:
   git checkout -b feature-branch  # Tạo branch mới
   git checkout main              # Chuyển về branch main
   git merge feature-branch       # Merge branch

5. 🛠️  XỬ LÝ CONFLICT:
   - Khi có conflict, sửa file bị conflict
   - git add .
   - git commit -m "Resolve conflicts"

📝 LỆNH THƯỜNG DÙNG:
   git status                    # Xem trạng thái
   git log --oneline            # Xem lịch sử commit
   git remote -v                # Xem remote repositories
   git branch -a                # Xem tất cả branch
   git fetch origin             # Fetch updates (không merge)
   git pull origin main         # Fetch + merge từ main branch
   git push origin main         # Push lên main branch

⚠️  LƯU Ý:
   - Luôn pull trước khi push
   - Commit thường xuyên với message rõ ràng
   - Sử dụng branch cho feature mới
   - Backup code quan trọng
""")


def main():
    """Hàm chính"""
    if not kiem_tra_git():
        input("Nhấn Enter để thoát...")
        return

    while True:
        hien_thi_menu()
        lua_chon = input("Chọn tùy chọn [0-9]: ").strip()

        if lua_chon == "0":
            print("👋 Tạm biệt!")
            break

        elif lua_chon == "1":
            khoi_tao_git_repo()

        elif lua_chon == "2":
            url = input(
                "Nhập URL repository (VD: https://github.com/se-info/prj1.git): ").strip()
            if url:
                them_remote_origin(url)

        elif lua_chon == "3":
            branch = input(
                "Nhập tên branch (Enter = main): ").strip() or "main"
            pull_tu_remote(branch)

        elif lua_chon == "4":
            branch = input(
                "Nhập tên branch (Enter = main): ").strip() or "main"
            push_len_remote(branch)

        elif lua_chon == "5":
            url = input("Nhập URL repository để clone: ").strip()
            thu_muc = input(
                "Nhập tên thư mục (Enter = tự động): ").strip() or None
            if url:
                clone_repository(url, thu_muc)

        elif lua_chon == "6":
            xem_trang_thai_git()

        elif lua_chon == "7":
            xem_lich_su_commit()

        elif lua_chon == "8":
            quan_ly_branch()

        elif lua_chon == "9":
            huong_dan_git_workflow()

        else:
            print("❌ Tùy chọn không hợp lệ!")

        if lua_chon != "0":
            input("\nNhấn Enter để tiếp tục...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Đã hủy")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        input("Nhấn Enter để thoát...")
