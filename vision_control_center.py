#!/usr/bin/env python3
# coding: utf-8
"""
Raspbot V2 Vision Control Center
Unified GUI launcher for all vision features
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import sys


class VisionControlCenter:
    """Main GUI control center for vision system"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Raspbot V2 - Vision Control Center")
        self.root.geometry("900x700")
        self.root.configure(bg='#1e3c72')
        
        # Running process
        self.current_process = None
        self.log_thread = None
        self.running = False
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        
        # Header
        header_frame = tk.Frame(self.root, bg='#2a5298', pady=20)
        header_frame.pack(fill=tk.X)
        
        title_label = tk.Label(
            header_frame,
            text="🤖 Raspbot V2 Vision System",
            font=('Arial', 24, 'bold'),
            bg='#2a5298',
            fg='white'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            header_frame,
            text="AI-Powered Camera Vision Control Center",
            font=('Arial', 12),
            bg='#2a5298',
            fg='#b3d9ff'
        )
        subtitle_label.pack()
        
        # Main container
        main_frame = tk.Frame(self.root, bg='#1e3c72', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Quick Launch
        left_panel = tk.LabelFrame(
            main_frame,
            text="🚀 Quick Launch",
            font=('Arial', 14, 'bold'),
            bg='#2a5298',
            fg='white',
            padx=15,
            pady=15
        )
        left_panel.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        
        # Web Viewer (Big button)
        web_btn = tk.Button(
            left_panel,
            text="🌐 Web Viewer\n(Recommended)",
            font=('Arial', 14, 'bold'),
            bg='#4fc3f7',
            fg='white',
            activebackground='#29b6f6',
            command=self.launch_web_viewer,
            height=3,
            cursor='hand2'
        )
        web_btn.pack(fill=tk.X, pady=(0, 15))
        
        # Headless Mode
        headless_frame = tk.LabelFrame(
            left_panel,
            text="Headless Mode (SSH)",
            font=('Arial', 11, 'bold'),
            bg='#2a5298',
            fg='white',
            padx=10,
            pady=10
        )
        headless_frame.pack(fill=tk.X, pady=(0, 15))
        
        headless_buttons = [
            ("👤 Face Recognition", "face"),
            ("👋 Gesture Detection", "gesture"),
            ("📦 3D Object Detection", "3d_object"),
        ]
        
        for text, mode in headless_buttons:
            btn = tk.Button(
                headless_frame,
                text=text,
                font=('Arial', 10),
                bg='#5c6bc0',
                fg='white',
                activebackground='#3949ab',
                command=lambda m=mode: self.launch_headless(m),
                cursor='hand2'
            )
            btn.pack(fill=tk.X, pady=3)
        
        # Recording options
        record_frame = tk.LabelFrame(
            left_panel,
            text="📹 Video Recording",
            font=('Arial', 11, 'bold'),
            bg='#2a5298',
            fg='white',
            padx=10,
            pady=10
        )
        record_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.duration_var = tk.StringVar(value="30")
        duration_frame = tk.Frame(record_frame, bg='#2a5298')
        duration_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(
            duration_frame,
            text="Duration (sec):",
            bg='#2a5298',
            fg='white',
            font=('Arial', 9)
        ).pack(side=tk.LEFT)
        
        duration_entry = tk.Entry(
            duration_frame,
            textvariable=self.duration_var,
            width=8,
            font=('Arial', 10)
        )
        duration_entry.pack(side=tk.LEFT, padx=5)
        
        record_btn = tk.Button(
            record_frame,
            text="● Record Video",
            font=('Arial', 10, 'bold'),
            bg='#ff5252',
            fg='white',
            activebackground='#ff1744',
            command=self.launch_video_record,
            cursor='hand2'
        )
        record_btn.pack(fill=tk.X, pady=(5, 0))
        
        # Right panel - Status & Log
        right_panel = tk.Frame(main_frame, bg='#1e3c72')
        right_panel.grid(row=0, column=1, sticky='nsew')
        
        # Status
        status_frame = tk.LabelFrame(
            right_panel,
            text="📊 Status",
            font=('Arial', 12, 'bold'),
            bg='#2a5298',
            fg='white',
            padx=10,
            pady=10
        )
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=('Arial', 11),
            bg='#2a5298',
            fg='#4fc3f7'
        )
        self.status_label.pack()
        
        # Log output
        log_frame = tk.LabelFrame(
            right_panel,
            text="📝 Output Log",
            font=('Arial', 12, 'bold'),
            bg='#2a5298',
            fg='white',
            padx=10,
            pady=10
        )
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            font=('Courier', 9),
            bg='#0d1b2a',
            fg='#00ff00',
            insertbackground='white',
            height=15
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Control buttons
        control_frame = tk.Frame(right_panel, bg='#1e3c72', pady=10)
        control_frame.pack(fill=tk.X)
        
        self.stop_btn = tk.Button(
            control_frame,
            text="⏹ Stop",
            font=('Arial', 11, 'bold'),
            bg='#ff5252',
            fg='white',
            activebackground='#ff1744',
            command=self.stop_process,
            state=tk.DISABLED,
            cursor='hand2'
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        clear_btn = tk.Button(
            control_frame,
            text="🗑 Clear Log",
            font=('Arial', 11),
            bg='#5c6bc0',
            fg='white',
            activebackground='#3949ab',
            command=self.clear_log,
            cursor='hand2'
        )
        clear_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        # Configure grid weights
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_rowconfigure(0, weight=1)
        
        self.log("Vision Control Center initialized")
        self.log("Click a button to launch vision features")
    
    def log(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def clear_log(self):
        """Clear log output"""
        self.log_text.delete(1.0, tk.END)
    
    def update_status(self, status, color='#4fc3f7'):
        """Update status label"""
        self.status_label.config(text=status, fg=color)
    
    def launch_web_viewer(self):
        """Launch web viewer"""
        if self.running:
            messagebox.showwarning("Already Running", "Please stop the current process first")
            return
        
        self.log("\n" + "="*50)
        self.log("🌐 Starting Web Viewer...")
        self.log("="*50)
        
        cmd = [sys.executable, "vision_web_viewer.py"]
        self.run_process(cmd, "Web Viewer Running")
        
        self.log("\n📱 Access the web interface:")
        self.log("   http://raspberrypi:5000")
        self.log("   http://raspberrypi.local:5000")
        self.log("   http://localhost:5000")
    
    def launch_headless(self, mode):
        """Launch headless mode"""
        if self.running:
            messagebox.showwarning("Already Running", "Please stop the current process first")
            return
        
        self.log("\n" + "="*50)
        self.log(f"🎯 Starting Headless Mode: {mode.upper()}")
        self.log("="*50)
        
        duration = self.duration_var.get()
        cmd = [
            sys.executable,
            "vision_system_headless.py",
            "--mode", mode,
            "--duration", duration
        ]
        
        self.run_process(cmd, f"Headless {mode} Running")
    
    def launch_video_record(self):
        """Launch video recording"""
        if self.running:
            messagebox.showwarning("Already Running", "Please stop the current process first")
            return
        
        mode = messagebox.askquestion(
            "Select Mode",
            "Record Face Detection?\n\n"
            "Yes = Face Detection\n"
            "No = Choose Other Mode"
        )
        
        if mode == 'yes':
            selected_mode = 'face'
        else:
            # Show options
            options = ['gesture', '3d_object']
            choice = messagebox.askquestion(
                "Select Mode",
                "Gesture Detection?\n\nYes = Gesture\nNo = 3D Object"
            )
            selected_mode = 'gesture' if choice == 'yes' else '3d_object'
        
        self.log("\n" + "="*50)
        self.log(f"📹 Recording video: {selected_mode}")
        self.log("="*50)
        
        duration = self.duration_var.get()
        cmd = [
            sys.executable,
            "vision_system_headless.py",
            "--mode", selected_mode,
            "--duration", duration,
            "--save-video"
        ]
        
        self.run_process(cmd, f"Recording {selected_mode}")
    
    def run_process(self, cmd, status_text):
        """Run a subprocess"""
        self.running = True
        self.stop_btn.config(state=tk.NORMAL)
        self.update_status(status_text, '#66bb6a')
        
        def run():
            try:
                self.current_process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # Read output
                for line in self.current_process.stdout:
                    if not self.running:
                        break
                    self.log(line.rstrip())
                
                self.current_process.wait()
                
                if self.running:
                    self.log("\n✅ Process completed")
                    self.update_status("Completed", '#4fc3f7')
                
            except Exception as e:
                self.log(f"\n❌ Error: {str(e)}")
                self.update_status("Error", '#ff5252')
            
            finally:
                self.running = False
                self.stop_btn.config(state=tk.DISABLED)
                self.current_process = None
        
        self.log_thread = threading.Thread(target=run, daemon=True)
        self.log_thread.start()
    
    def stop_process(self):
        """Stop running process"""
        if self.current_process:
            self.log("\n⏹ Stopping process...")
            self.current_process.terminate()
            self.running = False
            self.stop_btn.config(state=tk.DISABLED)
            self.update_status("Stopped", '#ff9800')
    
    def on_closing(self):
        """Handle window close"""
        if self.running:
            if messagebox.askokcancel("Quit", "Process is running. Stop and quit?"):
                self.stop_process()
                self.root.destroy()
        else:
            self.root.destroy()


def main():
    """Main entry point"""
    # Change to script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    root = tk.Tk()
    app = VisionControlCenter(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
