import tkinter as tk
import time
from pathlib import Path
from datetime import datetime
import os

class TransparentLogOverlay:
    def __init__(self):
        # Find most recent log file
        log_dir = Path("logs")
        if not log_dir.exists():
            raise FileNotFoundError("Logs directory not found")
            
        log_files = list(log_dir.glob("gemini_desk_*.log"))
        if not log_files:
            raise FileNotFoundError("No log files found in logs directory")
            
        self.log_file = str(max(log_files, key=lambda x: x.stat().st_ctime))
        print(f"Monitoring most recent log: {self.log_file}")

        self.root = tk.Tk()
        self.root.title("Log Overlay")
        
        # Make window transparent and always on top
        self.root.attributes('-alpha', 0.7)  # 70% opacity
        self.root.attributes('-topmost', True)
        
        # Remove window decorations
        self.root.overrideredirect(True)
        
        # Set initial position (top-right corner)
        self.root.geometry("400x300+{}+0".format(
            self.root.winfo_screenwidth() - 400))
        
        # Create text widget for logs
        self.log_text = tk.Text(self.root, bg='black', fg='lime',
                               font=('Consolas', 10), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add a close button
        close_btn = tk.Button(self.root, text="×", command=self.root.quit,
                            bg='black', fg='white')
        close_btn.place(x=380, y=0)
        
        # Make window draggable
        self.log_text.bind('<Button-1>', self.start_move)
        self.log_text.bind('<B1-Motion>', self.do_move)
        
        # Initialize monitoring variables
        self.last_position = 0
        self.last_size = 0
        
        # Start monitoring
        self.monitor_logs()

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def monitor_logs(self):
        try:
            # Check if file exists and has been modified
            current_size = Path(self.log_file).stat().st_size
            if current_size > self.last_size:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    f.seek(self.last_position)
                    new_lines = f.read()
                    self.log_text.insert(tk.END, new_lines)
                    self.log_text.see(tk.END)  # Auto-scroll to bottom
                    self.last_position = f.tell()
                self.last_size = current_size
                
            # Keep only last 50 lines
            lines = self.log_text.get('1.0', tk.END).splitlines()
            if len(lines) > 50:
                self.log_text.delete('1.0', tk.END)
                self.log_text.insert(tk.END, '\n'.join(lines[-50:]) + '\n')
                
        except Exception as e:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_text.insert(tk.END, f"\n[{current_time}] Error reading log: {str(e)}\n")
        
        # Check again after 100ms
        self.root.after(100, self.monitor_logs)

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    overlay = TransparentLogOverlay()
    overlay.run()
