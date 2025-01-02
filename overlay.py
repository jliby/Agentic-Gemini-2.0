from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QScrollArea, QTextEdit, QSizeGrip
from PyQt5.QtCore import Qt, QPoint, QTimer, QSize, QRect
from PyQt5.QtGui import QPalette, QColor, QCursor
import sys
import os
import glob
from live_api_starter_desk import CONFIG

class Overlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.dragging = False
        self.resizing = False
        self.offset = QPoint()
        self.last_position = 0
        
        # Set window flags and attributes
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint |
            Qt.WindowMaximizeButtonHint |  # Enable resizing
            Qt.Tool  # Makes it a utility window that stays on top
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_MacAlwaysShowToolWindow)  # Specific for macOS to ensure window stays visible
        self.setGeometry(100, 100, 400, 500)
        self.setWindowTitle("Gemini Live")  # Add window title
        
        # Create main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setCentralWidget(main_widget)

        # Create chat container with background
        chat_container = QWidget()
        chat_container.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 53, 65, 0.60);
                border-radius: 15px;
            }
        """)
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(15, 15, 15, 15)
        chat_layout.setSpacing(10)

        # Create top button container
        top_container = QWidget()
        top_layout = QHBoxLayout(top_container)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(10)

        # Add title label first (on the left)
        title_label = QLabel("Gemini Live")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
        """)
        top_layout.addWidget(title_label)

        # Add voice button
        current_voice = CONFIG["generation_config"]["speech_config"]
        test_button = QPushButton(f"{current_voice}")  # Using the first voice from voices list
        test_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(64, 65, 79, 0.95);
                border: none;
                border-radius: 8px;
                color: white;
                padding: 5px 15px;
                font-size: 14px;
                max-width: 60px;
            }
            QPushButton:hover {
                background-color: rgba(80, 81, 95, 0.95);
            }
        """)
        top_layout.addWidget(test_button)

        # Add spacer to push buttons to the right
        top_layout.addStretch()

        # Add minimize button
        minimize_button = QPushButton("−")
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #8e8e8e;
                padding: 5px;
                font-size: 20px;
                min-width: 30px;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        minimize_button.clicked.connect(self.showMinimized)
        top_layout.addWidget(minimize_button)

        # Add maximize button
        maximize_button = QPushButton("□")
        maximize_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #8e8e8e;
                padding: 5px;
                font-size: 16px;
                min-width: 30px;
            }
            QPushButton:hover {
                color: #ffffff;
            }
        """)
        maximize_button.clicked.connect(self.toggleMaximize)
        top_layout.addWidget(maximize_button)
        
        # Add close button
        close_button = QPushButton("×")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #8e8e8e;
                padding: 5px;
                font-size: 20px;
                min-width: 30px;
            }
            QPushButton:hover {
                color: #ff4d4d;
            }
        """)
        close_button.clicked.connect(QApplication.instance().quit)
        top_layout.addWidget(close_button)

        chat_layout.addWidget(top_container, alignment=Qt.AlignRight)

        # Create scrollable chat display
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: rgba(64, 65, 79, 0.5);
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: rgba(255, 255, 255, 0.3);
                border-radius: 4px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                border: none;
                background: none;
                color: none;
            }
        """)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                color: white;
                background-color: transparent;
                border: none;
                font-size: 14px;
                selection-background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        scroll_area.setWidget(self.chat_display)
        chat_layout.addWidget(scroll_area)

        # Create input container
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background-color: rgba(64, 65, 79, 0.95);
                border-radius: 10px;
                margin: 10px;
            }
        """)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)

        # Create input field
        self.input_field = QLineEdit()
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: none;
                color: white;
                padding: 5px;
                font-size: 14px;
            }
        """)
        self.input_field.setPlaceholderText("Message Gemini...")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        # Create clear input button
        clear_input_button = QPushButton("×")  # Changed from "✕" to "×" for a cleaner look
        clear_input_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #8e8e8e;
                padding: 2px;
                font-size: 16px;
                min-width: 16px;
                margin-right: -5px;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        clear_input_button.clicked.connect(self.input_field.clear)
        input_layout.addWidget(clear_input_button)

        # Create send button
        send_button = QPushButton("➤")
        send_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                color: #8e8e8e;
                padding: 5px;
                font-size: 18px;
                min-width: 30px;
            }
            QPushButton:hover {
                color: white;
            }
        """)
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(send_button)

        chat_layout.addWidget(input_container)
        main_layout.addWidget(chat_container)

        # Add size grip for resizing
        size_grip = QSizeGrip(self)
        size_grip.setStyleSheet("""
            QSizeGrip {
                background-color: rgba(255, 255, 255, 0.1);
                width: 16px;
                height: 16px;
                border-radius: 8px;
            }
            QSizeGrip:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        
        # Create a container for the size grip
        grip_container = QWidget(self)
        grip_layout = QHBoxLayout(grip_container)
        grip_layout.setContentsMargins(0, 0, 0, 0)
        grip_layout.addStretch()
        grip_layout.addWidget(size_grip)
        
        # Add the grip container to the main layout
        main_layout.addWidget(grip_container, 0, Qt.AlignRight | Qt.AlignBottom)

        # Set minimum size for the window
        self.setMinimumSize(300, 400)

        # Set up log file monitoring
        self.logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_chat_display)
        self.timer.start(1000)  # Check for updates every second

    def get_latest_log_file(self):
        log_files = glob.glob(os.path.join(self.logs_dir, '*.log'))
        if not log_files:
            return None
        return max(log_files, key=os.path.getctime)

    def update_chat_display(self):
        log_file = self.get_latest_log_file()
        if not log_file:
            return

        try:
            with open(log_file, 'r') as f:
                # Read all lines and get the last 50
                lines = f.readlines()
                recent_lines = lines[-50:] if len(lines) > 50 else lines
                
                # Update the display with the recent lines
                self.chat_display.clear()
                self.chat_display.setText(''.join(recent_lines))
                
                # Scroll to bottom
                self.chat_display.verticalScrollBar().setValue(
                    self.chat_display.verticalScrollBar().maximum()
                )
                
                # Update position to end of file
                self.last_position = f.tell()
        except Exception as e:
            print(f"Error reading log file: {e}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            rect = self.rect()
            edge_size = 10
            pos = event.pos()
            
            # Check if we're on the edge (for resizing)
            if (pos.x() >= rect.width() - edge_size or 
                pos.y() >= rect.height() - edge_size):
                self.resizing = True
                self.resize_start_pos = pos
                self.resize_start_size = self.size()
                event.accept()
                return
            
            self.dragging = True
            self.offset = pos

    def mouseMoveEvent(self, event):
        rect = self.rect()
        edge_size = 10
        pos = event.pos()
        
        # Handle resizing
        if self.resizing and event.buttons() == Qt.LeftButton:
            diff = pos - self.resize_start_pos
            new_width = max(self.minimumWidth(), self.resize_start_size.width() + diff.x())
            new_height = max(self.minimumHeight(), self.resize_start_size.height() + diff.y())
            self.resize(new_width, new_height)
            return
        
        # Handle resize cursor
        if (pos.x() >= rect.width() - edge_size and 
            pos.y() >= rect.height() - edge_size):
            self.setCursor(Qt.SizeFDiagCursor)
        elif pos.x() >= rect.width() - edge_size:
            self.setCursor(Qt.SizeHorCursor)
        elif pos.y() >= rect.height() - edge_size:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            
        # Handle dragging
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + pos - self.offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.resizing = False
            self.setCursor(Qt.ArrowCursor)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Update the layout when resizing
        self.update()

    def toggleMaximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def send_message(self):
        message = self.input_field.text().strip()
        if message:
            try:
                # Write message to queue file
                with open('message_queue.txt', 'a', encoding='utf-8') as f:
                    f.write(message + '\n')
                    f.flush()  # Ensure message is written immediately
                os.fsync(f.fileno())  # Force write to disk
                
                # Add message to chat display
                self.add_message("You: " + message)
                
                # Clear input field
                self.input_field.clear()
            except Exception as e:
                print(f"Error sending message: {e}")

    def add_message(self, message):
        self.chat_display.append(message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    overlay = Overlay()
    overlay.show()
    sys.exit(app.exec_())
