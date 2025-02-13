"""
Medical AI Suite - Professional Medical Interface
This application provides a modern interface for medical AI assistance and ECG analysis.
Author: [Dhia Eddine Ayachi from Innovation Academy]
Version: 1.0
"""

import sys
import pandas as pd
import subprocess
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                           QLineEdit, QLabel, QFrame, QStatusBar, 
                           QToolButton, QMenu, QAction)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap

# Get the directory of the current script
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

def launch_ecg_analysis():
    """Launch the ECG analysis tool in a separate process."""
    ecg_tool_path = os.path.join(CURRENT_DIR, 'appcode.py')
    if os.path.exists(ecg_tool_path):
        subprocess.Popen([sys.executable, ecg_tool_path])
    else:
        print(f"Error: Could not find ECG analysis tool at {ecg_tool_path}")

class QuickActionButton(QPushButton):
    def __init__(self, text, color="#4A90E2"):
        super().__init__(text)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 15px;
                padding: 8px 20px;
                font-size: 13px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {color}DD;
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)

class ChatbotWidget(QWidget):
    """
    Main chat interface widget that handles all chat-related functionality.
    Includes message display, input handling, and chat history management.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Main layout setup with zero margins for modern look
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header section with gradient background and professional styling
        self._create_header(layout)
        
        # Main chat area with message display
        self._create_chat_area(layout)
        
        # Input section with send functionality
        self._create_input_area(layout)
        
        self.setLayout(layout)

    def _create_header(self, layout):
        """Creates the header section with title, status, and settings."""
        # Header container with gradient
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #1A237E, stop:0.5 #0D47A1, stop:1 #01579B);
                border-top-left-radius: 20px;
                border-top-right-radius: 20px;
                border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Doctor icon with container
        self._add_doctor_icon(header_layout)
        
        # Title and status section
        self._add_title_and_status(header_layout)
        
        # Settings button with menu
        self._add_settings_button(header_layout)
        
        layout.addWidget(header)

    def _add_doctor_icon(self, layout):
        """Adds the doctor icon to the header."""
        icon_container = QFrame()
        icon_container.setFixedSize(40, 40)
        icon_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                padding: 8px;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel("👨‍⚕️")
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        layout.addWidget(icon_container)

    def _add_title_and_status(self, layout):
        """Adds the title and status indicator to the header."""
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(10, 0, 0, 0)
        title_layout.setSpacing(2)
        
        title = QLabel("Medical AI Assistant")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title)
        
        status = QLabel("● Active")
        status.setStyleSheet("color: #4CAF50; font-size: 12px;")
        title_layout.addWidget(status)
        
        layout.addWidget(title_container, stretch=1)

    def _add_settings_button(self, layout):
        """Adds the settings button with menu to the header."""
        settings_btn = QToolButton()
        settings_btn.setText("⚙️")
        settings_btn.setFont(QFont("Segoe UI Emoji", 16))
        settings_btn.setStyleSheet("""
            QToolButton {
                color: white;
                background: transparent;
                border: none;
                padding: 5px;
                border-radius: 15px;
            }
            QToolButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        
        menu = QMenu(settings_btn)
        menu.addAction("Clear History")
        menu.addAction("Quick Responses")
        menu.addAction("Language")
        menu.addAction("Theme")
        settings_btn.setMenu(menu)
        settings_btn.setPopupMode(QToolButton.InstantPopup)
        
        layout.addWidget(settings_btn)

    def _create_chat_area(self, layout):
        """Creates the main chat display area with custom styling."""
        chat_container = QFrame()
        chat_container.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                          stop:0 #F5F7FA, stop:1 #E8EEF5);
                border: none;
            }
        """)
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        # Chat display with custom scrollbar
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Start your medical consultation here...")
        self._set_chat_display_style()
        chat_layout.addWidget(self.chat_display)
        
        layout.addWidget(chat_container)

    def _create_input_area(self, layout):
        """Creates the input area with message field and send button."""
        # Input container with modern design
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-bottom-left-radius: 20px;
                border-bottom-right-radius: 20px;
                padding: 15px;
                border-top: 1px solid #E0E0E0;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 10, 15, 10)
        
        # Input field container with focus effects
        self._add_input_field(input_layout)
        
        layout.addWidget(input_frame)

    def _set_chat_display_style(self):
        """Sets the style for the chat display area."""
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: none;
                padding: 15px;
                font-size: 14px;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

    def _add_input_field(self, layout):
        """Adds the input field and send button."""
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #E0E0E0;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
                background: white;
            }
            QLineEdit:focus {
                border-color: #2196F3;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)
        
        send_btn = QPushButton("➤")
        send_btn.setFont(QFont("Segoe UI Symbol", 14))
        send_btn.setFixedSize(40, 40)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        layout.addWidget(send_btn)

    def _display_user_message(self, message):
        """Displays the user's message in the chat."""
        self.chat_display.append(f'<div style="margin: 10px 0px; text-align: right;">'
                               f'<span style="background: #E3F2FD; color: #1565C0; padding: 10px 15px; '
                               f'border-radius: 15px 15px 0px 15px; display: inline-block; '
                               f'max-width: 70%; text-align: left;">'
                               f'{message}</span></div>')

    def _display_ai_response(self):
        """Displays the AI's response in the chat."""
        response = "I am here to help with your medical questions. How can I assist you today?"
        self.chat_display.append(f'<div style="margin: 10px 0px;">'
                               f'<span style="background: #F5F5F5; color: #424242; padding: 10px 15px; '
                               f'border-radius: 15px 15px 15px 0px; display: inline-block; '
                               f'max-width: 70%;">'
                               f'{response}</span></div>')

    def _scroll_to_bottom(self):
        """Scrolls the chat display to show the latest message."""
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):
        """Handles sending and displaying messages in the chat."""
        message = self.input_field.text()
        if message:
            # Display user message with styling
            self._display_user_message(message)
            self.input_field.clear()
            
            # Display AI response with styling
            self._display_ai_response()
            
            # Auto-scroll to latest message
            self._scroll_to_bottom()

class MainWindow(QMainWindow):
    """
    Main application window that contains the chat widget and tools panel.
    Handles the overall layout and tool integration.
    """
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Window setup
        self.setWindowTitle('Medical AI Suite')
        self.setGeometry(100, 100, 1200, 800)
        self._set_window_style()

        # Main layout setup
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Content area with chat and tools
        self._create_content_area(main_layout)

    def _set_window_style(self):
        """Sets the main window's background and style."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #34495E;
            }
            QToolTip {
                background-color: #2C3E50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 13px;
            }
        """)

    def _set_tools_panel_style(self, panel):
        """Sets the style for the tools panel."""
        panel.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-radius: 15px;
                padding: 20px;
            }
        """)

    def _add_tools_header(self, layout):
        """Adds the tools section header and description."""
        tools_header = QLabel("Medical Tools")
        tools_header.setFont(QFont("Segoe UI", 24, QFont.Bold))
        tools_header.setStyleSheet("color: white; margin-bottom: 10px;")
        layout.addWidget(tools_header)
        
        tools_desc = QLabel("Advanced ECG analysis and processing tools")
        tools_desc.setStyleSheet("color: #BDC3C7; font-size: 14px;")
        tools_desc.setWordWrap(True)
        layout.addWidget(tools_desc)

    def _add_tool_buttons(self, layout):
        """Adds the tool buttons to the panel."""
        button_style = """
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2980B9;
                transform: scale(1.02);
            }
            QPushButton:pressed {
                background-color: #2475A8;
            }
        """
        
        # ECG Analysis button
        ecg_analysis_btn = QPushButton("🔬 ECG Analysis")
        ecg_analysis_btn.setStyleSheet(button_style)
        ecg_analysis_btn.setCursor(Qt.PointingHandCursor)
        ecg_analysis_btn.setMinimumHeight(80)
        ecg_analysis_btn.clicked.connect(launch_ecg_analysis)
        layout.addWidget(ecg_analysis_btn)
        
        # Signal Processing button
        signal_proc_btn = QPushButton("📊 Signal Processing")
        signal_proc_btn.setStyleSheet(button_style)
        signal_proc_btn.setCursor(Qt.PointingHandCursor)
        signal_proc_btn.setMinimumHeight(80)
        layout.addWidget(signal_proc_btn)
        
        layout.addStretch()

    def _add_status_indicator(self, layout):
        """Adds the status indicator to the bottom of the tools panel."""
        status_label = QLabel("System Status: Online")
        status_label.setStyleSheet("""
            QLabel {
                color: #2ECC71;
                font-size: 13px;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """)
        layout.addWidget(status_label)

    def _create_content_area(self, main_layout):
        """Creates the main content area with chat and tools panels."""
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(20)
        
        # Add chat interface
        chatbot = ChatbotWidget()
        content_layout.addWidget(chatbot, stretch=2)

        # Add tools panel
        self._add_tools_panel(content_layout)
        
        main_layout.addWidget(content_widget)

    def _add_tools_panel(self, content_layout):
        """Creates the tools panel with ECG analysis features."""
        right_panel = QFrame()
        self._set_tools_panel_style(right_panel)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(20)
        
        # Add tools header and description
        self._add_tools_header(right_layout)
        
        # Add tool buttons
        self._add_tool_buttons(right_layout)
        
        # Add status indicator
        self._add_status_indicator(right_layout)
        
        content_layout.addWidget(right_panel, stretch=1)

if __name__ == '__main__':
    # Initialize application
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 12))
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 