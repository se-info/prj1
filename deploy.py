#!/usr/bin/env python3
"""
Deployment script for Crypto Order Block Detector
Supports multiple hosting platforms: Heroku, Railway, Render, and Local
"""

import os
import subprocess
import sys
import json


def run_command(command, capture_output=True):
    """Run a shell command and return the result"""
    try:
        if capture_output:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        else:
            result = subprocess.run(command, shell=True)
            return result.returncode == 0, "", ""
    except Exception as e:
        return False, "", str(e)


def check_dependencies():
    """Check if required tools are installed"""
    print("🔍 Checking dependencies...")

    # Check Python
    success, stdout, stderr = run_command("python --version")
    if success:
        print(f"✅ Python: {stdout.strip()}")
    else:
        print("❌ Python not found")
        return False

    # Check Git
    success, stdout, stderr = run_command("git --version")
    if success:
        print(f"✅ Git: {stdout.strip()}")
    else:
        print("❌ Git not found")
        return False

    return True


def install_requirements():
    """Install Python requirements"""
    print("\n📦 Installing requirements...")
    success, stdout, stderr = run_command("pip install -r requirements.txt")
    if success:
        print("✅ Requirements installed successfully")
        return True
    else:
        print(f"❌ Failed to install requirements: {stderr}")
        return False


def test_local():
    """Test the application locally"""
    print("\n🧪 Testing application locally...")
    print("Starting Flask app on http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)

    # Run the app (this will block until Ctrl+C)
    success, stdout, stderr = run_command(
        "python app.py", capture_output=False)
    return success


def deploy_heroku():
    """Deploy to Heroku"""
    print("\n🚀 Deploying to Heroku...")

    # Check if Heroku CLI is installed
    success, stdout, stderr = run_command("heroku --version")
    if not success:
        print("❌ Heroku CLI not found. Please install it from https://devcenter.heroku.com/articles/heroku-cli")
        return False

    print(f"✅ Heroku CLI: {stdout.strip()}")

    # Login to Heroku
    print("Please login to Heroku...")
    success, stdout, stderr = run_command("heroku login", capture_output=False)
    if not success:
        print("❌ Failed to login to Heroku")
        return False

    # Get app name from user
    app_name = input(
        "Enter your Heroku app name (or press Enter for auto-generated): ").strip()

    # Create Heroku app
    if app_name:
        create_cmd = f"heroku create {app_name}"
    else:
        create_cmd = "heroku create"

    success, stdout, stderr = run_command(create_cmd)
    if success:
        print(f"✅ Heroku app created: {stdout.strip()}")
    else:
        print(f"⚠️ App creation result: {stderr}")

    # Initialize git if not already
    if not os.path.exists('.git'):
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "Initial commit"')

    # Add Heroku remote and deploy
    run_command("git add .")
    run_command('git commit -m "Deploy to Heroku"')
    success, stdout, stderr = run_command("git push heroku main")

    if success:
        print("✅ Successfully deployed to Heroku!")
        run_command("heroku open")
        return True
    else:
        print(f"❌ Deployment failed: {stderr}")
        return False


def deploy_railway():
    """Deploy to Railway"""
    print("\n🚄 Deploying to Railway...")
    print("1. Go to https://railway.app")
    print("2. Sign up/Login with GitHub")
    print("3. Click 'New Project'")
    print("4. Select 'Deploy from GitHub repo'")
    print("5. Choose your repository")
    print("6. Railway will automatically detect Python and deploy")
    print("7. Your app will be available at the provided URL")
    input("Press Enter to continue...")


def deploy_render():
    """Deploy to Render"""
    print("\n🎨 Deploying to Render...")
    print("1. Go to https://render.com")
    print("2. Sign up/Login with GitHub")
    print("3. Click 'New' > 'Web Service'")
    print("4. Connect your GitHub repository")
    print("5. Use these settings:")
    print("   - Environment: Python 3")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: gunicorn app:app")
    print("6. Click 'Create Web Service'")
    input("Press Enter to continue...")


def create_docker_files():
    """Create Docker files for containerized deployment"""
    print("\n🐳 Creating Docker files...")

    # Create Dockerfile
    dockerfile_content = """FROM python:3.11.7-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
"""

    with open('Dockerfile', 'w') as f:
        f.write(dockerfile_content)

    # Create docker-compose.yml
    compose_content = """version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
"""

    with open('docker-compose.yml', 'w') as f:
        f.write(compose_content)

    print("✅ Created Dockerfile and docker-compose.yml")
    print("To run with Docker:")
    print("  docker-compose up --build")


def main():
    """Main deployment script"""
    print("🚀 Crypto Order Block Detector - Deployment Script")
    print("=" * 55)

    if not check_dependencies():
        sys.exit(1)

    while True:
        print("\nChoose deployment option:")
        print("1. Test locally")
        print("2. Deploy to Heroku")
        print("3. Deploy to Railway (instructions)")
        print("4. Deploy to Render (instructions)")
        print("5. Create Docker files")
        print("6. Install requirements only")
        print("0. Exit")

        choice = input("\nEnter your choice (0-6): ").strip()

        if choice == '0':
            print("👋 Goodbye!")
            break
        elif choice == '1':
            if install_requirements():
                test_local()
        elif choice == '2':
            if install_requirements():
                deploy_heroku()
        elif choice == '3':
            deploy_railway()
        elif choice == '4':
            deploy_render()
        elif choice == '5':
            create_docker_files()
        elif choice == '6':
            install_requirements()
        else:
            print("❌ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
