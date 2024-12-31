import win32api
import win32con
import win32gui
import time
import threading

from ctypes import windll, pointer
from ctypes.wintypes import MSG


class MyWindow:
    _window_instance = None

    def __init__(self):
        # Ensure single instance
        if MyWindow._window_instance:
            raise Exception("Window already exists!")
        MyWindow._window_instance = self
        
        self.count = 10
        win32gui.InitCommonControls()
        self.hinst = win32api.GetModuleHandle(None)
        className = 'MyWndClass'
        message_map = {
            win32con.WM_DESTROY: self.OnDestroy,
            win32con.WM_PAINT: self.OnPaint,
            win32con.WM_ERASEBKGND: self.OnEraseBkgnd,
        }
        wc = win32gui.WNDCLASS()
        wc.style = win32con.CS_HREDRAW | win32con.CS_VREDRAW
        wc.lpfnWndProc = message_map
        wc.lpszClassName = className
        win32gui.RegisterClass(wc)
        
        # Add layered and transparent window styles
        style = win32con.WS_POPUP
        ex_style = win32con.WS_EX_LAYERED | win32con.WS_EX_TRANSPARENT | win32con.WS_EX_TOPMOST
        
        # Create window in a fixed position
        self.hwnd = win32gui.CreateWindowEx(
            ex_style,
            className,
            'Transparent Window',
            style,
            100, 100,  # Fixed position x, y
            300, 300,  # Width, height
            0,
            0,
            self.hinst,
            None
        )
        
        # Set window transparency (alpha value: 128 out of 255)
        win32gui.SetLayeredWindowAttributes(self.hwnd, 0, 128, win32con.LWA_ALPHA)
        
        win32gui.UpdateWindow(self.hwnd)
        win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)

        # Start countdown thread
        self.running = True
        self.countdown_thread = threading.Thread(target=self.countdown)
        self.countdown_thread.daemon = True  # Make thread daemon so it exits with main thread
        self.countdown_thread.start()

    def countdown(self):
        while self.running and self.count > 0:
            time.sleep(1)
            self.count -= 1
            # Hide window
            win32gui.ShowWindow(self.hwnd, win32con.SW_HIDE)
            # Force complete repaint
            win32gui.InvalidateRect(self.hwnd, None, True)
            win32gui.UpdateWindow(self.hwnd)
            # Show window again
            win32gui.ShowWindow(self.hwnd, win32con.SW_SHOW)
            win32gui.SetForegroundWindow(self.hwnd)
        if self.running:
            win32gui.PostMessage(self.hwnd, win32con.WM_CLOSE, 0, 0)

    def OnDestroy(self, hwnd, message, wparam, lparam):
        self.running = False
        MyWindow._window_instance = None
        win32gui.PostQuitMessage(0)
        return True

    def OnEraseBkgnd(self, hwnd, message, wparam, lparam):
        # Handle background erasure to prevent flickering
        return True

    def OnPaint(self, hwnd, message, wparam, lparam):
        hdc, ps = win32gui.BeginPaint(hwnd)
        
        # Set text properties
        win32gui.SetTextColor(hdc, win32api.RGB(255, 255, 255))  # White text
        win32gui.SetBkMode(hdc, win32con.TRANSPARENT)
        
        # Get client area for text positioning
        rect = win32gui.GetClientRect(hwnd)
        
        # Draw countdown text
        text = str(self.count)
        win32gui.DrawText(hdc, text, -1, rect, 
                         win32con.DT_CENTER | win32con.DT_VCENTER | win32con.DT_SINGLELINE)
        
        win32gui.EndPaint(hwnd, ps)
        return True


def main():
    try:
        window = MyWindow()
        msg = MSG()
        lpmsg = pointer(msg)

        print('Entering message loop')
        while windll.user32.GetMessageA(lpmsg, 0, 0, 0) != 0:
            windll.user32.TranslateMessage(lpmsg)
            windll.user32.DispatchMessageA(lpmsg)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        print('done.')


if __name__ == "__main__":
    main()