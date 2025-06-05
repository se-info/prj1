#!/usr/bin/env python3
"""
Demo Runner for Local Network Chat Room
Helps users test the chat application easily.
"""

import subprocess
import threading
import time
import sys
import os


def run_server():
    """Run the chat server."""
    print("Starting chat server...")
    try:
        subprocess.run([sys.executable, "chat_server.py"], check=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
    except Exception as e:
        print(f"Server error: {e}")


def run_client():
    """Run a chat client."""
    print("Starting chat client...")
    try:
        subprocess.run([sys.executable, "chat_client.py"], check=True)
    except Exception as e:
        print(f"Client error: {e}")


def main():
    """Main demo function."""
    print("=== Local Network Chat Room Demo ===")
    print()
    print("This demo will help you test the chat application.")
    print()
    print("Choose an option:")
    print("1. Start server only")
    print("2. Start client only")
    print("3. Start server and client (for testing)")
    print("4. Exit")
    print()

    while True:
        try:
            choice = input("Enter your choice (1-4): ").strip()

            if choice == "1":
                print("\nStarting server...")
                print("Press Ctrl+C to stop the server")
                run_server()
                break

            elif choice == "2":
                print("\nStarting client...")
                print("Make sure the server is running on the target machine")
                run_client()
                break

            elif choice == "3":
                print("\nStarting server and client for local testing...")
                print("The server will start first, then a client window will open")
                print("Press Ctrl+C in this window to stop the server")
                print()

                # Start server in a separate thread
                server_thread = threading.Thread(
                    target=run_server, daemon=True)
                server_thread.start()

                # Wait a moment for server to start
                time.sleep(2)

                # Start client in a separate process
                try:
                    subprocess.Popen([sys.executable, "chat_client.py"])
                    print(
                        "Client started. You can start additional clients by running:")
                    print(f"python {os.path.join('.', 'chat_client.py')}")
                    print()
                    print("Press Ctrl+C to stop the server...")

                    # Keep main thread alive to handle Ctrl+C
                    server_thread.join()

                except KeyboardInterrupt:
                    print("\nDemo stopped.")

                break

            elif choice == "4":
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")

        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
