#!/usr/bin/env python3
"""
Local Network Chat Room Client
GUI client with text messaging, emoji, sticker, and image support.
"""

import socket
import json
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import datetime
import base64
from PIL import Image, ImageTk
import io


class ChatClient:
    def __init__(self):
        self.socket = None
        self.nickname = None
        self.connected = False

        # GUI setup
        self.root = tk.Tk()
        self.root.title("Local Network Chat Room")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # GUI variables
        self.chat_text = None
        self.message_entry = None
        self.user_listbox = None
        self.send_button = None

        # Emoji data
        self.emojis = [
            "😀", "😁", "😂", "🤣", "😃", "😄", "😅", "😆", "😉", "😊",
            "😋", "😎", "😍", "😘", "🥰", "😗", "😙", "😚", "🙂", "🤗",
            "🤔", "😐", "😑", "😶", "🙄", "😏", "😣", "😥", "😮", "🤐",
            "😯", "😪", "😫", "😴", "😌", "😛", "😜", "😝", "🤤", "😒",
            "😓", "😔", "😕", "🙃", "🤑", "😲", "🙁", "😖", "😞", "😟",
            "👍", "👎", "👌", "✌️", "🤞", "🤟", "🤘", "🤙", "👈", "👉",
            "👆", "👇", "☝️", "✋", "🤚", "🖐️", "🖖", "👋", "🤝", "🙏",
            "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔",
            "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝", "💟", "☮️"
        ]

        # Sticker data (simple text representations)
        self.stickers = {
            "happy": "ヽ(°〇°)ﾉ",
            "love": "(♡°▽°♡)",
            "cool": "( ͡° ͜ʖ ͡°)",
            "surprised": "(⊙_⊙)",
            "sad": "(╥﹏╥)",
            "angry": "(╬ಠ益ಠ)",
            "thinking": "( ͡° ͜ʖ ͡°)",
            "party": "\\(^o^)/",
            "sleepy": "(-.-)zzZ",
            "confused": "(´･ω･`)"
        }

        self.setup_gui()

    def setup_gui(self):
        """Set up the main GUI interface."""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Connection frame
        conn_frame = ttk.LabelFrame(main_frame, text="Connection", padding=10)
        conn_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(conn_frame, text="Server IP:").grid(
            row=0, column=0, sticky=tk.W)
        self.host_entry = ttk.Entry(conn_frame, width=15)
        self.host_entry.insert(0, "localhost")
        self.host_entry.grid(row=0, column=1, padx=(5, 10))

        ttk.Label(conn_frame, text="Port:").grid(row=0, column=2, sticky=tk.W)
        self.port_entry = ttk.Entry(conn_frame, width=8)
        self.port_entry.insert(0, "12345")
        self.port_entry.grid(row=0, column=3, padx=(5, 10))

        self.connect_button = ttk.Button(
            conn_frame, text="Connect", command=self.connect_to_server)
        self.connect_button.grid(row=0, column=4, padx=(10, 0))

        self.disconnect_button = ttk.Button(
            conn_frame, text="Disconnect", command=self.disconnect, state=tk.DISABLED)
        self.disconnect_button.grid(row=0, column=5, padx=(5, 0))

        # Chat area frame
        chat_frame = ttk.Frame(main_frame)
        chat_frame.pack(fill=tk.BOTH, expand=True)

        # Left side - Chat and input
        left_frame = ttk.Frame(chat_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Chat display
        chat_label_frame = ttk.LabelFrame(left_frame, text="Chat", padding=5)
        chat_label_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        # Chat text area with scrollbar
        chat_scroll_frame = ttk.Frame(chat_label_frame)
        chat_scroll_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_text = tk.Text(chat_scroll_frame, state=tk.DISABLED, wrap=tk.WORD,
                                 font=("Arial", 10), bg="white", fg="black")
        chat_scrollbar = ttk.Scrollbar(
            chat_scroll_frame, orient=tk.VERTICAL, command=self.chat_text.yview)
        self.chat_text.configure(yscrollcommand=chat_scrollbar.set)

        self.chat_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Message input frame
        input_frame = ttk.LabelFrame(
            left_frame, text="Send Message", padding=5)
        input_frame.pack(fill=tk.X)

        # Message entry
        message_frame = ttk.Frame(input_frame)
        message_frame.pack(fill=tk.X, pady=(0, 5))

        self.message_entry = ttk.Entry(message_frame, state=tk.DISABLED)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X,
                                expand=True, padx=(0, 5))
        self.message_entry.bind("<Return>", self.send_text_message)

        self.send_button = ttk.Button(
            message_frame, text="Send", command=self.send_text_message, state=tk.DISABLED)
        self.send_button.pack(side=tk.RIGHT)

        # Buttons frame
        buttons_frame = ttk.Frame(input_frame)
        buttons_frame.pack(fill=tk.X)

        self.emoji_button = ttk.Button(
            buttons_frame, text="😀 Emoji", command=self.show_emoji_picker, state=tk.DISABLED)
        self.emoji_button.pack(side=tk.LEFT, padx=(0, 5))

        self.sticker_button = ttk.Button(
            buttons_frame, text="🎭 Sticker", command=self.show_sticker_picker, state=tk.DISABLED)
        self.sticker_button.pack(side=tk.LEFT, padx=(0, 5))

        self.image_button = ttk.Button(
            buttons_frame, text="🖼️ Image", command=self.send_image, state=tk.DISABLED)
        self.image_button.pack(side=tk.LEFT)

        # Right side - Users list
        right_frame = ttk.LabelFrame(
            chat_frame, text="Online Users", padding=5)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, ipadx=10)

        # Users listbox with scrollbar
        users_scroll_frame = ttk.Frame(right_frame)
        users_scroll_frame.pack(fill=tk.BOTH, expand=True)

        self.user_listbox = tk.Listbox(
            users_scroll_frame, width=20, font=("Arial", 9))
        users_scrollbar = ttk.Scrollbar(
            users_scroll_frame, orient=tk.VERTICAL, command=self.user_listbox.yview)
        self.user_listbox.configure(yscrollcommand=users_scrollbar.set)

        self.user_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        users_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Disconnected")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(10, 0))

    def connect_to_server(self):
        """Connect to the chat server."""
        if self.connected:
            return

        host = self.host_entry.get().strip()
        try:
            port = int(self.port_entry.get().strip())
        except ValueError:
            messagebox.showerror("Error", "Invalid port number")
            return

        if not host:
            messagebox.showerror("Error", "Please enter server IP")
            return

        try:
            # Create socket and connect
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((host, port))

            # Start receiving thread
            receive_thread = threading.Thread(
                target=self.receive_messages, daemon=True)
            receive_thread.start()

            self.connected = True
            self.status_var.set(f"Connected to {host}:{port}")

            # Update UI
            self.connect_button.config(state=tk.DISABLED)
            self.disconnect_button.config(state=tk.NORMAL)
            self.host_entry.config(state=tk.DISABLED)
            self.port_entry.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect: {e}")
            self.socket = None

    def disconnect(self):
        """Disconnect from the server."""
        if not self.connected:
            return

        self.connected = False

        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None

        self.nickname = None

        # Update UI
        self.status_var.set("Disconnected")
        self.connect_button.config(state=tk.NORMAL)
        self.disconnect_button.config(state=tk.DISABLED)
        self.host_entry.config(state=tk.NORMAL)
        self.port_entry.config(state=tk.NORMAL)

        self.message_entry.config(state=tk.DISABLED)
        self.send_button.config(state=tk.DISABLED)
        self.emoji_button.config(state=tk.DISABLED)
        self.sticker_button.config(state=tk.DISABLED)
        self.image_button.config(state=tk.DISABLED)

        self.user_listbox.delete(0, tk.END)
        self.add_to_chat("SYSTEM", "Disconnected from server", "system")

    def receive_messages(self):
        """Receive messages from the server."""
        buffer = ""

        while self.connected:
            try:
                data = self.socket.recv(4096).decode('utf-8')
                if not data:
                    break

                buffer += data

                # Process complete messages (each ends with \n)
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    if line.strip():
                        try:
                            message = json.loads(line.strip())
                            self.handle_server_message(message)
                        except json.JSONDecodeError:
                            print(f"Invalid JSON received: {line}")

            except Exception as e:
                if self.connected:
                    print(f"Error receiving message: {e}")
                break

        if self.connected:
            self.root.after(0, self.disconnect)

    def handle_server_message(self, message):
        """Handle different types of messages from the server."""
        msg_type = message.get("type", "")

        if msg_type == "nickname_request":
            self.root.after(0, self.prompt_nickname)

        elif msg_type == "nickname_accepted":
            self.nickname = message.get("nickname")
            self.root.after(0, self.enable_chat)
            self.root.after(0, lambda: self.add_to_chat(
                "SYSTEM", f"Welcome, {self.nickname}!", "system"))

        elif msg_type == "nickname_error":
            error_msg = message.get("message", "Nickname error")
            self.root.after(0, lambda: messagebox.showerror(
                "Nickname Error", error_msg))
            self.root.after(0, self.prompt_nickname)

        elif msg_type == "text":
            nickname = message.get("nickname", "Unknown")
            content = message.get("content", "")
            self.root.after(0, lambda: self.add_to_chat(
                nickname, content, "text"))

        elif msg_type == "emoji":
            nickname = message.get("nickname", "Unknown")
            emoji = message.get("emoji", "")
            self.root.after(0, lambda: self.add_to_chat(
                nickname, emoji, "emoji"))

        elif msg_type == "sticker":
            nickname = message.get("nickname", "Unknown")
            sticker_id = message.get("sticker_id", "")
            sticker_text = self.stickers.get(sticker_id, f"[{sticker_id}]")
            self.root.after(0, lambda: self.add_to_chat(
                nickname, sticker_text, "sticker"))

        elif msg_type == "image":
            nickname = message.get("nickname", "Unknown")
            image_data = message.get("image_data", "")
            image_name = message.get("image_name", "image.png")
            self.root.after(0, lambda: self.display_image_message(
                nickname, image_data, image_name))

        elif msg_type == "system":
            system_msg = message.get("message", "")
            self.root.after(0, lambda: self.add_to_chat(
                "SYSTEM", system_msg, "system"))

        elif msg_type == "user_list":
            users = message.get("users", [])
            self.root.after(0, lambda: self.update_user_list(users))

    def prompt_nickname(self):
        """Prompt user for nickname."""
        nickname = simpledialog.askstring(
            "Nickname", "Enter your nickname:", parent=self.root)
        if nickname and self.connected:
            try:
                message = json.dumps({"nickname": nickname.strip()})
                self.socket.send(message.encode('utf-8') + b'\n')
            except:
                self.disconnect()
        elif self.connected:
            self.disconnect()

    def enable_chat(self):
        """Enable chat interface after successful nickname setup."""
        self.message_entry.config(state=tk.NORMAL)
        self.send_button.config(state=tk.NORMAL)
        self.emoji_button.config(state=tk.NORMAL)
        self.sticker_button.config(state=tk.NORMAL)
        self.image_button.config(state=tk.NORMAL)
        self.message_entry.focus()

    def add_to_chat(self, nickname, content, msg_type="text"):
        """Add a message to the chat display."""
        self.chat_text.config(state=tk.NORMAL)

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        if msg_type == "system":
            self.chat_text.insert(
                tk.END, f"[{timestamp}] *** {content} ***\n", "system")
        else:
            if msg_type == "emoji":
                self.chat_text.insert(
                    tk.END, f"[{timestamp}] {nickname}: {content}\n", "emoji")
            elif msg_type == "sticker":
                self.chat_text.insert(
                    tk.END, f"[{timestamp}] {nickname} sent sticker: {content}\n", "sticker")
            else:
                self.chat_text.insert(
                    tk.END, f"[{timestamp}] {nickname}: {content}\n", "text")

        # Configure tags for styling
        self.chat_text.tag_configure(
            "system", foreground="blue", font=("Arial", 9, "italic"))
        self.chat_text.tag_configure(
            "emoji", foreground="orange", font=("Arial", 12))
        self.chat_text.tag_configure(
            "sticker", foreground="purple", font=("Arial", 10, "bold"))

        self.chat_text.config(state=tk.DISABLED)
        self.chat_text.see(tk.END)

    def display_image_message(self, nickname, image_data, image_name):
        """Display an image message in the chat."""
        try:
            # Decode base64 image data
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))

            # Resize image for display (thumbnail)
            image.thumbnail((200, 200), Image.Resampling.LANCZOS)

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)

            # Add to chat
            self.chat_text.config(state=tk.NORMAL)
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            self.chat_text.insert(
                tk.END, f"[{timestamp}] {nickname} sent image: {image_name}\n")
            self.chat_text.image_create(tk.END, image=photo)
            self.chat_text.insert(tk.END, "\n")

            # Keep a reference to prevent garbage collection
            if not hasattr(self, 'image_refs'):
                self.image_refs = []
            self.image_refs.append(photo)

            self.chat_text.config(state=tk.DISABLED)
            self.chat_text.see(tk.END)

        except Exception as e:
            self.add_to_chat(
                "SYSTEM", f"Error displaying image from {nickname}: {e}", "system")

    def update_user_list(self, users):
        """Update the online users list."""
        self.user_listbox.delete(0, tk.END)
        for user in sorted(users):
            self.user_listbox.insert(tk.END, user)

    def send_text_message(self, event=None):
        """Send a text message."""
        if not self.connected or not self.nickname:
            return

        content = self.message_entry.get().strip()
        if not content:
            return

        try:
            message = {
                "type": "text",
                "content": content,
                "nickname": self.nickname
            }

            self.socket.send(json.dumps(message).encode('utf-8') + b'\n')

            # Add to own chat display
            self.add_to_chat(self.nickname, content, "text")

            # Clear input
            self.message_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
            self.disconnect()

    def show_emoji_picker(self):
        """Show emoji picker window."""
        if not self.connected:
            return

        emoji_window = tk.Toplevel(self.root)
        emoji_window.title("Choose Emoji")
        emoji_window.geometry("400x300")
        emoji_window.resizable(False, False)

        # Create frame with scrollbar
        canvas = tk.Canvas(emoji_window)
        scrollbar = ttk.Scrollbar(
            emoji_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Add emojis in grid
        row, col = 0, 0
        for emoji in self.emojis:
            btn = tk.Button(scrollable_frame, text=emoji, font=("Arial", 16),
                            command=lambda e=emoji: self.send_emoji(
                                e, emoji_window),
                            width=3, height=1)
            btn.grid(row=row, column=col, padx=2, pady=2)

            col += 1
            if col >= 10:
                col = 0
                row += 1

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def send_emoji(self, emoji, window):
        """Send an emoji message."""
        try:
            message = {
                "type": "emoji",
                "emoji": emoji,
                "nickname": self.nickname
            }

            self.socket.send(json.dumps(message).encode('utf-8') + b'\n')

            # Add to own chat display
            self.add_to_chat(self.nickname, emoji, "emoji")

            window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send emoji: {e}")
            self.disconnect()

    def show_sticker_picker(self):
        """Show sticker picker window."""
        if not self.connected:
            return

        sticker_window = tk.Toplevel(self.root)
        sticker_window.title("Choose Sticker")
        sticker_window.geometry("300x400")
        sticker_window.resizable(False, False)

        # Create sticker buttons
        row = 0
        for sticker_id, sticker_text in self.stickers.items():
            btn = tk.Button(sticker_window, text=f"{sticker_id}\n{sticker_text}",
                            font=("Arial", 10), width=20, height=2,
                            command=lambda sid=sticker_id: self.send_sticker(sid, sticker_window))
            btn.grid(row=row, column=0, padx=10, pady=5, sticky="ew")
            row += 1

    def send_sticker(self, sticker_id, window):
        """Send a sticker message."""
        try:
            message = {
                "type": "sticker",
                "sticker_id": sticker_id,
                "nickname": self.nickname
            }

            self.socket.send(json.dumps(message).encode('utf-8') + b'\n')

            # Add to own chat display
            sticker_text = self.stickers.get(sticker_id, f"[{sticker_id}]")
            self.add_to_chat(self.nickname, sticker_text, "sticker")

            window.destroy()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send sticker: {e}")
            self.disconnect()

    def send_image(self):
        """Send an image file."""
        if not self.connected:
            return

        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        try:
            # Check file size (limit to 1MB)
            import os
            file_size = os.path.getsize(file_path)
            if file_size > 1024 * 1024:  # 1MB
                messagebox.showerror(
                    "Error", "Image file is too large (max 1MB)")
                return

            # Read and encode image
            with open(file_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')

            image_name = os.path.basename(file_path)

            message = {
                "type": "image",
                "image_data": image_data,
                "image_name": image_name,
                "nickname": self.nickname
            }

            self.socket.send(json.dumps(message).encode('utf-8') + b'\n')

            # Add to own chat display
            self.display_image_message(self.nickname, image_data, image_name)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send image: {e}")

    def on_closing(self):
        """Handle window closing."""
        if self.connected:
            self.disconnect()
        self.root.destroy()

    def run(self):
        """Start the client application."""
        self.root.mainloop()


def main():
    """Main function to start the client."""
    print("=== Local Network Chat Room Client ===")

    try:
        # Check if PIL is available
        import PIL
    except ImportError:
        print("Warning: PIL (Pillow) not found. Image features will not work.")
        print("Install with: pip install Pillow")

    client = ChatClient()
    client.run()


if __name__ == "__main__":
    main()
