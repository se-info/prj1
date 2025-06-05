#!/usr/bin/env python3
"""
Local Test Runner for Crypto Analysis Application
This file helps test the app functionality locally without deploying.
"""

import os
import sys
import requests
import time
import threading
import json
from datetime import datetime

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the Flask app
from app import app, OrderBlockDetector, UserLogger

class LocalAppTester:
    """Test runner for local development"""
    
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        self.app_running = False
        
    def start_app(self):
        """Start the Flask app in a separate thread"""
        def run_app():
            app.run(host=self.host, port=self.port, debug=False, use_reloader=False)
            
        print(f"🚀 Starting Flask app on {self.base_url}")
        app_thread = threading.Thread(target=run_app, daemon=True)
        app_thread.start()
        
        # Wait for app to start
        for i in range(10):
            try:
                response = requests.get(f"{self.base_url}/", timeout=2)
                if response.status_code == 200:
                    self.app_running = True
                    print(f"✅ App started successfully on {self.base_url}")
                    return True
            except requests.exceptions.RequestException:
                time.sleep(1)
                
        print("❌ Failed to start app")
        return False
    
    def test_home_page(self):
        """Test the home page"""
        try:
            response = requests.get(f"{self.base_url}/")
            print(f"📄 Home page: {response.status_code} - {'✅ OK' if response.status_code == 200 else '❌ Error'}")
            return response.status_code == 200
        except Exception as e:
            print(f"📄 Home page: ❌ Error - {e}")
            return False
    
    def test_symbols_api(self):
        """Test symbols API endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/symbols")
            print(f"💱 Symbols API: {response.status_code} - {'✅ OK' if response.status_code == 200 else '❌ Error'}")
            if response.status_code == 200:
                symbols = response.json()
                print(f"    Found {len(symbols)} symbols")
            return response.status_code == 200
        except Exception as e:
            print(f"💱 Symbols API: ❌ Error - {e}")
            return False
    
    def test_login_api(self):
        """Test login API endpoint"""
        try:
            login_data = {"username": "testuser"}
            response = requests.post(f"{self.base_url}/api/login", json=login_data)
            print(f"🔐 Login API: {response.status_code} - {'✅ OK' if response.status_code == 200 else '❌ Error'}")
            return response.status_code == 200
        except Exception as e:
            print(f"🔐 Login API: ❌ Error - {e}")
            return False
    
    def test_analysis_api(self):
        """Test analysis API endpoint"""
        try:
            analysis_data = {
                "symbol": "BTC/USDT",
                "timeframe": "1h",
                "username": "testuser"
            }
            print("📊 Testing Analysis API (this may take a moment)...")
            response = requests.post(f"{self.base_url}/api/analyze", json=analysis_data, timeout=30)
            print(f"📊 Analysis API: {response.status_code} - {'✅ OK' if response.status_code == 200 else '❌ Error'}")
            if response.status_code == 200:
                result = response.json()
                print(f"    Analysis completed for {analysis_data['symbol']}")
            return response.status_code == 200
        except Exception as e:
            print(f"📊 Analysis API: ❌ Error - {e}")
            return False
    
    def test_order_block_detector_direct(self):
        """Test OrderBlockDetector class directly"""
        print("🔍 Testing OrderBlockDetector directly...")
        try:
            detector = OrderBlockDetector()
            print("  ✅ OrderBlockDetector initialized")
            
            # Test with sample data
            df = detector.generate_sample_data("BTC/USDT")
            if df is not None and len(df) > 0:
                print(f"  ✅ Sample data generated: {len(df)} candles")
                
                # Test order block detection
                order_blocks = detector.detect_order_blocks(df)
                print(f"  ✅ Order blocks detected: {len(order_blocks)}")
                
                # Test trading signals
                signals = detector.generate_trading_signals(df)
                print(f"  ✅ Trading signals generated: {len(signals)} signals")
                return True
            else:
                print("  ❌ Failed to generate sample data")
                return False
        except Exception as e:
            print(f"  ❌ OrderBlockDetector test failed: {e}")
            return False
    
    def test_user_logger_direct(self):
        """Test UserLogger class directly"""
        print("📝 Testing UserLogger directly...")
        try:
            logger = UserLogger()
            print("  ✅ UserLogger initialized")
            
            # Test logging activity
            logger.log_activity(
                username="testuser",
                action="test_action", 
                symbol="BTC/USDT",
                details="Testing local app"
            )
            print("  ✅ Activity logged successfully")
            
            # Test getting user stats
            stats = logger.get_user_stats("testuser")
            print(f"  ✅ User stats retrieved: {stats.get('total_activities', 0)} activities")
            return True
        except Exception as e:
            print(f"  ❌ UserLogger test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("=" * 60)
        print("🧪 LOCAL CRYPTO ANALYSIS APP TESTER")
        print("=" * 60)
        
        # Start the app
        if not self.start_app():
            print("❌ Cannot start app, aborting tests")
            return False
        
        time.sleep(2)  # Give app time to fully start
        
        print("\n🧪 Testing API Endpoints:")
        # Run API tests
        self.test_home_page()
        self.test_symbols_api()
        self.test_login_api()
        self.test_analysis_api()
        
        print("\n🔧 Testing Core Components:")
        # Run direct component tests
        self.test_order_block_detector_direct()
        self.test_user_logger_direct()
        
        print("\n" + "=" * 60)
        print("🎉 LOCAL TESTING COMPLETED")
        print("=" * 60)
        print(f"📱 App is running at: {self.base_url}")
        print("🔧 Press Ctrl+C to stop the app")
        
        return True
    
    def show_available_endpoints(self):
        """Show available endpoints for manual testing"""
        print("\n📋 Available endpoints for manual testing:")
        print(f"   • Home page: {self.base_url}/")
        print(f"   • Symbols: {self.base_url}/api/symbols")
        print(f"   • Analysis: POST {self.base_url}/api/analyze")
        print(f"   • Login: POST {self.base_url}/api/login")
        print("\n📝 Sample POST request for analysis:")
        print(json.dumps({
            "symbol": "BTC/USDT",
            "timeframe": "1h", 
            "username": "testuser"
        }, indent=2))

def main():
    """Main function to run tests"""
    tester = LocalAppTester()
    
    try:
        success = tester.run_all_tests()
        if success:
            tester.show_available_endpoints()
            print("\n🖱️  You can now manually test the app in your browser!")
            
            # Keep running until user stops
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Stopping app...")
                
    except Exception as e:
        print(f"❌ Test runner failed: {e}")

if __name__ == "__main__":
    main()
