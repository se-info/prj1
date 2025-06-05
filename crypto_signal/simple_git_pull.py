#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Git Pull Script
Thực hiện: git remote add origin + git pull
"""

import subprocess
import sys


def run_git_command(command):
    """Chạy lệnh git"""
    print(f"▶️ {command}")
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )

        if result.stdout.strip():
            print(f"✅ {result.stdout.strip()}")

        if result.stderr.strip() and result.returncode != 0:
            print(f"⚠️ {result.stderr.strip()}")

        return result.returncode == 0

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Main function"""
    print("🔧 Git Remote Add + Pull Script")
    print("=" * 40)

    # Repository URL từ yêu cầu của bạn
    repo_url = "https://github.com/se-info/prj1.git"

    print(f"📂 Repository: {repo_url}")
    print()

    # Bước 1: Thêm remote origin (như bạn đã đề cập)
    print("1️⃣ Thêm remote origin...")
    run_git_command(f"git remote add origin {repo_url}")

    # Bước 2: Fetch để cập nhật thông tin
    print("\n2️⃣ Fetch từ remote...")
    run_git_command("git fetch origin")

    # Bước 3: Pull code từ main branch
    print("\n3️⃣ Pull từ remote...")
    success = run_git_command("git pull origin main")

    if success:
        print("\n🎉 Hoàn thành!")
    else:
        # Nếu pull main thất bại, thử master
        print("\n🔄 Thử pull từ master branch...")
        run_git_command("git pull origin master")

    # Hiển thị trạng thái
    print("\n📊 Trạng thái hiện tại:")
    run_git_command("git status")


if __name__ == "__main__":
    main()
