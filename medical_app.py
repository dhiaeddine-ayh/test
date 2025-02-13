"""
Medical AI Suite - Professional Medical Interface
This application provides a modern interface for medical AI assistance and ECG analysis.
Author: [Dhia Eddine Ayachi from Innovation Academy]
Version: 1.0
"""

import sys
import pandas as pd
import cv2
import numpy as np
from PIL import Image, ImageQt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                           QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                           QLineEdit, QLabel, QFrame, QStatusBar, 
                           QToolButton, QMenu, QAction, QStackedWidget,
                           QGraphicsView, QGraphicsScene, QFileDialog,
                           QMessageBox, QDialog, QComboBox, QSizePolicy,
                           QRubberBand)
from PyQt5.QtCore import Qt, QSize, QTimer, QRectF, QRect
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QImage, QPainter, QPen, QBrush
import os
import csv

# Import necessary variables and functions from test3.py
rectangles = []
drawing = False
ix, iy = -1, -1
current_rectangle = None
selected_rectangle = None
img = None
img_original_size = (0, 0)
img_resized_size = (1260, 900)
image_loaded = False
opened_image_path = None
zoom_factor = 1.0
zoom_step = 0.3
min_zoom = 1.0
max_zoom = 4.0
rotation_angle = 0
offset_x = offset_y = 0

# Add these to the global variables at the top
rectangle_history = []
current_history_index = -1

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
        # Main layout setup with modern styling
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Header section with gradient background
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                                          stop:0 #2C3E50, stop:1 #3498DB);
                border-top-left-radius: 15px;
                border-top-right-radius: 15px;
                border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            }
        """)
        header.setMinimumHeight(80)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Doctor icon with container
        icon_container = QFrame()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 25px;
                padding: 8px;
            }
        """)
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel("👨‍⚕️")
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_layout.addWidget(icon_label)
        
        header_layout.addWidget(icon_container)
        
        # Title and status section
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        title_layout.setContentsMargins(10, 0, 0, 0)
        title_layout.setSpacing(2)
        
        title = QLabel("Medical AI Assistant")
        title.setStyleSheet("""
            color: white;
            font-size: 18px;
            font-weight: bold;
        """)
        title_layout.addWidget(title)
        
        status = QLabel("● Active")
        status.setStyleSheet("""
            color: #2ECC71;
            font-size: 13px;
        """)
        title_layout.addWidget(status)
        
        header_layout.addWidget(title_container, stretch=1)
        
        # Settings button
        settings_btn = QPushButton("⚙️")
        settings_btn.setFont(QFont("Segoe UI Emoji", 16))
        settings_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background: transparent;
                border: none;
                padding: 5px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.1);
            }
        """)
        header_layout.addWidget(settings_btn)
        
        layout.addWidget(header)
        
        # Chat display area
        chat_container = QFrame()
        chat_container.setStyleSheet("""
            QFrame {
                background: white;
                border: none;
            }
        """)
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(0, 0, 0, 0)
        
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("Start your medical consultation here...")
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: none;
                padding: 20px;
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
        chat_layout.addWidget(self.chat_display)
        
        layout.addWidget(chat_container)
        
        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-bottom-left-radius: 15px;
                border-bottom-right-radius: 15px;
                padding: 15px;
                border-top: 1px solid #E0E0E0;
            }
        """)
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(15, 10, 15, 10)
        
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
                border-color: #3498DB;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)
        
        send_btn = QPushButton("➤")
        send_btn.setFont(QFont("Segoe UI Symbol", 14))
        send_btn.setFixedSize(40, 40)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border-radius: 20px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
            QPushButton:pressed {
                background-color: #2475A8;
            }
        """)
        send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(send_btn)
        
        layout.addWidget(input_frame)

    def _display_user_message(self, message):
        """Displays the user's message in the chat."""
        self.chat_display.append(
            f'<div style="margin: 10px 0px; text-align: right;">'
            f'<span style="background: #3498DB; color: white; padding: 12px 18px; '
            f'border-radius: 18px 18px 0px 18px; display: inline-block; '
            f'max-width: 70%; text-align: left; font-size: 14px;">'
            f'{message}</span></div>'
        )

    def _display_ai_response(self):
        """Displays the AI's response in the chat."""
        response = "I am here to help with your medical questions. How can I assist you today?"
        self.chat_display.append(
            f'<div style="margin: 10px 0px;">'
            f'<span style="background: #F5F5F5; color: #2C3E50; padding: 12px 18px; '
            f'border-radius: 18px 18px 18px 0px; display: inline-block; '
            f'max-width: 70%; font-size: 14px;">'
            f'{response}</span></div>'
        )

    def _scroll_to_bottom(self):
        """Scrolls the chat display to show the latest message."""
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def send_message(self):
        """Handles sending and displaying messages in the chat."""
        message = self.input_field.text().strip()
        if message:
            self._display_user_message(message)
            self.input_field.clear()
            self._display_ai_response()
            self._scroll_to_bottom()

class InputDialog(QDialog):
    def __init__(self, parent=None, title="", label=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setStyleSheet("""
            QDialog {
                background-color: white;
                border-radius: 10px;
            }
            QLabel {
                font-size: 14px;
                color: #2C3E50;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #BDC3C7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498DB;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add label
        self.label = QLabel(label)
        layout.addWidget(self.label)
        
        # Add line edit
        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText("Enter name here...")
        layout.addWidget(self.lineEdit)
        
        # Add buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        button_layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #E74C3C;
            }
            QPushButton:hover {
                background-color: #C0392B;
            }
        """)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)

    def getValue(self):
        return self.lineEdit.text()

class ObservationDialog(QDialog):
    def __init__(self, img, rectangles, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Observation Interface")
        self.resize(1400, 800)
        self.setStyleSheet("background-color: white;")

        self.img = img
        self.rectangles = rectangles
        self.valid_selections = []
        self.observations_dict = {}
        self.valid_uploaded_files = []

        self.selected_name = None
        self.selected_image = None
        self.selected_class = "Select Class"
        self.selected_file_path = "No file uploaded"

        self.remaining_options = [name for _, _, _, _, name in rectangles]

        self.init_data()
        self.init_widgets()
        self.init_layout()

    def init_data(self):
        self.image_var = Qt.DisplayRole
        self.class_var = "Select Class"
        self.selected_file_path = "No file uploaded"

    def init_widgets(self):
        self.image_widget = QLabel()
        self.image_widget.setFixedSize(200, 100)
        self.image_widget.setStyleSheet("border: 1px solid black; background-color: white;")

        self.label_upload_file = QLabel("No file uploaded")
        self.label_upload_file.setStyleSheet("background-color: white;")

        self.dropdown_list_selection = QComboBox()
        self.dropdown_list_selection.addItems(self.remaining_options)
        self.dropdown_list_selection.setCurrentText("")
        self.dropdown_list_selection.currentIndexChanged.connect(self.on_selection_changed)
        self.dropdown_list_selection.currentIndexChanged.connect(self.on_selection_class_validate)

        self.dropdown_class_selection = QComboBox()
        self.dropdown_class_selection.addItems(["Class A", "Class B", "Class C", "Class D", "Unclassed"])
        self.dropdown_class_selection.currentIndexChanged.connect(self.on_selection_class_validate)

        self.text_observation_entry = QTextEdit()
        self.text_observation_entry.setStyleSheet("border: 1px solid black; background-color: white;")

        self.btn_valid = QPushButton("Valid")
        self.btn_valid.setStyleSheet("background-color: white;border: 2px solid black;")
        self.btn_valid.setEnabled(False)
        self.btn_valid.clicked.connect(self.on_validate)

        self.btn_upload = QPushButton("Upload File")
        self.btn_upload.setStyleSheet("background-color: white;border: 2px solid black;")
        self.btn_upload.clicked.connect(self.on_upload)

        self.btn_save = QPushButton("Save")
        self.btn_save.setStyleSheet("background-color: white;border: 2px solid black;")
        self.btn_save.setEnabled(False)
        self.btn_save.clicked.connect(self.on_save)

    def init_layout(self):
        layout_top = QHBoxLayout()
        layout_top.addWidget(QLabel("Select Rectangle:"), alignment=Qt.AlignLeft)
        layout_top.addWidget(self.dropdown_list_selection, alignment=Qt.AlignLeft)

        layout_image = QVBoxLayout()
        layout_image.addWidget(self.image_widget, alignment=Qt.AlignLeft)
        layout_top.addLayout(layout_image)

        layout_image_class = QHBoxLayout()
        layout_image_class.addWidget(QLabel("Select class:"), alignment=Qt.AlignLeft)
        layout_image_class.addWidget(self.dropdown_class_selection, alignment=Qt.AlignLeft)
        layout_top.addLayout(layout_image_class)

        layout_bottom = QHBoxLayout()
        layout_upload = QVBoxLayout()
        layout_upload.addWidget(QLabel("Observation:"), alignment=Qt.AlignLeft)
        layout_upload.addWidget(self.text_observation_entry, alignment=Qt.AlignLeft)
        layout_bottom.addLayout(layout_upload)

        layout_upload_file = QVBoxLayout()
        layout_upload_file.addWidget(QLabel("Upload File:"), alignment=Qt.AlignLeft)
        layout_upload_file.addWidget(self.label_upload_file, alignment=Qt.AlignLeft)
        layout_upload_file.addWidget(self.btn_upload, alignment=Qt.AlignLeft)
        layout_bottom.addLayout(layout_upload_file)

        layout_bottom_buttons = QHBoxLayout()
        layout_bottom_buttons.addWidget(self.btn_valid)
        layout_bottom_buttons.addWidget(self.btn_save)

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(layout_top)
        self.main_layout.addLayout(layout_bottom)
        self.main_layout.addLayout(layout_bottom_buttons)
        self.setLayout(self.main_layout)

    def on_selection_changed(self, value):
        selected_name = self.dropdown_list_selection.currentText()
        self.selected_name = selected_name
        for rect in self.rectangles:
            x1, y1, x2, y2, name = rect
            if name == selected_name:
                x1_resized = int(x1 * img_resized_size[0] / img_original_size[1])
                y1_resized = int(y1 * img_resized_size[1] / img_original_size[0])
                x2_resized = int(x2 * img_resized_size[0] / img_original_size[1])
                y2_resized = int(y2 * img_resized_size[1] / img_original_size[0])

                sub_image = img[y1_resized:y2_resized, x1_resized:x2_resized]
                sub_image = cv2.resize(sub_image, (200, 100))
                sub_image = cv2.cvtColor(sub_image, cv2.COLOR_BGR2RGB)
                h, w, ch = sub_image.shape
                bytes_per_line = ch * w
                q_img = QImage(sub_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.image_widget.setPixmap(pixmap)
                break

    def on_selection_class_validate(self):
        self.on_validate_button_enabled()

    def on_validate_button_enabled(self):
        is_selected_name = self.dropdown_list_selection.currentText()
        is_selected_class = self.dropdown_class_selection.currentText()
        is_selected_class = False if is_selected_class is None else True
        if not is_selected_name or not is_selected_class:
            self.btn_valid.setEnabled(False)
        else:
            self.btn_valid.setEnabled(True)

    def on_validate(self):
        selected_name = self.dropdown_list_selection.currentText()
        selected_class = self.dropdown_class_selection.currentText()
        observation_text = self.text_observation_entry.toPlainText()
        
        if selected_name not in self.observations_dict:
            self.observations_dict[selected_name] = {
                "observation": observation_text,
                "class": selected_class
            }
        if selected_name not in self.valid_selections:
            self.valid_selections.append(selected_name)

        if selected_name in self.remaining_options:
            self.remaining_options.remove(selected_name)
            self.update_dropdown()

        self.text_observation_entry.clear()
        self.on_save_button_enabled()

    def on_save_button_enabled(self):
        if len(self.valid_selections) > 0:
            self.btn_save.setEnabled(True)
        else:
            self.btn_save.setEnabled(False)

    def update_dropdown(self):
        self.dropdown_list_selection.clear()
        self.dropdown_list_selection.addItems(self.remaining_options)
        self.dropdown_list_selection.setCurrentText("")

    def on_upload(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select a File", "", "All Files (*.*)")
        if file_path:
            file_name = os.path.basename(file_path)
            self.selected_file_path = file_name
            self.label_upload_file.setText(f"Uploaded File: {file_name}")
            self.on_validate_button_enabled()

    def on_save(self):
        save_path = QFileDialog.getExistingDirectory(self, "Select Save Directory")
        if not save_path:
            return

        classes_dir = os.path.join(save_path, "classes")
        os.makedirs(classes_dir, exist_ok=True)

        for selected_name in self.valid_selections:
            observation_data = self.observations_dict.get(selected_name)
            if observation_data:
                observation_text = observation_data["observation"]
                selected_class = observation_data["class"]

                for rect in self.rectangles:
                    x1, y1, x2, y2, name = rect
                    if name == selected_name:
                        x1_resized = int(x1 * img_resized_size[0] / img_original_size[1])
                        y1_resized = int(y1 * img_resized_size[1] / img_original_size[0])
                        x2_resized = int(x2 * img_resized_size[0] / img_original_size[1])
                        y2_resized = int(y2 * img_resized_size[1] / img_original_size[0])

                        sub_image = img[y1_resized:y2_resized, x1_resized:x2_resized]
                        base_filename = os.path.join(save_path, f"{selected_name}.png")
                        rectangle_image_filename = base_filename

                        count = 1
                        unique_name = selected_name
                        while os.path.exists(rectangle_image_filename):
                            unique_name = f"{selected_name}_copy{count}"
                            rectangle_image_filename = os.path.join(save_path, f"{unique_name}.png")
                            count += 1

                        cv2.imwrite(rectangle_image_filename, sub_image)

                        if observation_text:
                            observation_filename = os.path.join(save_path, f"{unique_name}_observation.txt")
                            with open(observation_filename, "w") as obs_file:
                                obs_file.write(observation_text)

                        class_filename = os.path.join(classes_dir, f"{selected_class}.txt")
                        with open(class_filename, "a") as class_file:
                            class_file.write(f"{unique_name}, ")

                        break

        self.accept()

class DigitalizeDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Digitalize Lead")
        self.setMinimumSize(800, 600)
        
        self.processed_images = {}
        self.processed_signals = {}
        
        layout = QVBoxLayout(self)
        
        # Add list of rectangles
        self.rect_list = QComboBox()
        self.rect_list.addItems([rect[4] for rect in rectangles])
        layout.addWidget(self.rect_list)
        
        # Add preview area
        self.preview_widget = QLabel()
        layout.addWidget(self.preview_widget)
        
        # Add buttons
        btn_layout = QHBoxLayout()
        
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self.preview_selected)
        btn_layout.addWidget(preview_btn)
        
        digitalize_btn = QPushButton("Digitalize")
        digitalize_btn.clicked.connect(self.digitalize_selected)
        btn_layout.addWidget(digitalize_btn)
        
        save_btn = QPushButton("Save All")
        save_btn.clicked.connect(self.save_all)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)

    def preview_selected(self):
        name = self.rect_list.currentText()
        if not name:
            return
            
        for rect in rectangles:
            if rect[4] == name:
                x1, y1, x2, y2, _ = rect
                x1_resized = int(x1 * img_resized_size[0] / img_original_size[1])
                y1_resized = int(y1 * img_resized_size[1] / img_original_size[0])
                x2_resized = int(x2 * img_resized_size[0] / img_original_size[1])
                y2_resized = int(y2 * img_resized_size[1] / img_original_size[0])
                
                sub_image = img[y1_resized:y2_resized, x1_resized:x2_resized]
                self.processed_images[name] = sub_image
                
                # Display preview
                preview_img = cv2.cvtColor(sub_image, cv2.COLOR_BGR2RGB)
                h, w, ch = preview_img.shape
                bytes_per_line = ch * w
                q_img = QImage(preview_img.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.preview_widget.setPixmap(QPixmap.fromImage(q_img))
                break

    def digitalize_selected(self):
        name = self.rect_list.currentText()
        if name not in self.processed_images:
            return
            
        img = self.processed_images[name]
        
        # Process image
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 255, 220]))
        result = cv2.bitwise_and(img, img, mask=mask)
        result[mask == 0] = 255
        
        # Convert to grayscale and threshold
        gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Extract signal
        height, width = binary.shape
        signal_x = []
        signal_y = []
        
        for x in range(width):
            col = binary[:, x]
            points = np.where(col == 255)[0]
            if len(points) > 0:
                y = np.mean(points)
                signal_x.append(x)
                signal_y.append(y)
        
        self.processed_signals[name] = (signal_x, signal_y)
        
        # Show preview of digitalized signal
        plt.figure(figsize=(8, 4))
        plt.plot(signal_x, signal_y)
        plt.title(f"Digitalized Signal - {name}")
        plt.show()

    def save_all(self):
        if not self.processed_signals:
            QMessageBox.warning(self, "Warning", "No signals processed yet!")
            return
            
        save_dir = QFileDialog.getExistingDirectory(self, "Select Directory to Save Signals")
        if not save_dir:
            return
            
        for name, (x, y) in self.processed_signals.items():
            filename = os.path.join(save_dir, f"{name}_signal.csv")
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['x', 'y'])
                for xi, yi in zip(x, y):
                    writer.writerow([xi, yi])
                    
        QMessageBox.information(self, "Success", "All signals saved successfully!")
        self.accept()

class ECGAnalysisPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        self.init_ui()
        
        # Initialize drawing variables
        self.start_pos = None
        self.current_rect = None
        self.drawing = False
        
        # Initialize history
        global rectangle_history, current_history_index
        rectangle_history = [[] if not rectangles else rectangles.copy()]
        current_history_index = 0
        
    def init_ui(self):
        # Main layout with better responsiveness
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Left panel for buttons with fixed width
        left_panel = QFrame()
        left_panel.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border: none;
                min-width: 200px;
                max-width: 300px;
            }
        """)
        left_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(10)
        left_layout.setContentsMargins(10, 15, 10, 15)
        
        # Add controls to left panel
        self._create_left_panel_controls(left_layout)
        
        # Right panel for image view with expanding size
        right_panel = QFrame()
        right_panel.setStyleSheet("""
            QFrame {
                background-color: #ECF0F1;
                border: none;
            }
        """)
        right_panel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create graphics view with improved responsiveness
        self.scene = QGraphicsScene()
        self.graphics_view = QGraphicsView(self.scene)
        self.graphics_view.setRenderHints(QPainter.RenderHint.Antialiasing | 
                                        QPainter.RenderHint.SmoothPixmapTransform)
        self.graphics_view.setStyleSheet("""
            QGraphicsView {
                background-color: white;
                border: 2px solid #BDC3C7;
                border-radius: 10px;
            }
        """)
        self.graphics_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Enable mouse tracking for drawing
        self.graphics_view.setMouseTracking(True)
        self.graphics_view.viewport().installEventFilter(self)
        
        right_layout.addWidget(self.graphics_view)
        
        # Add panels to main layout with proper ratios
        main_layout.addWidget(left_panel, 2)  # 20% of width
        main_layout.addWidget(right_panel, 8)  # 80% of width

    def _create_left_panel_controls(self, layout):
        """Creates the controls for the left panel."""
        # Title
        title_label = QLabel("ECG Analysis")
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding-bottom: 10px;
                border-bottom: 2px solid #3498DB;
            }
        """)
        layout.addWidget(title_label)
        
        # Back button
        back_btn = QPushButton("← Back to Main")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        back_btn.clicked.connect(self.go_back_to_main)
        layout.addWidget(back_btn)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #34495E;")
        layout.addWidget(separator)
        
        # Control buttons
        buttons = [
            ("📂 Open Image", self.open_image),
            ("↩️ Undo", self.undo_action),
            ("↪️ Redo", self.redo_action),
            ("🔄 Reset Workspace", self.reset_workspace),
            ("🗑️ Delete Selection", self.delete_selected),
            ("💾 Save All Areas", self.save_all_areas),
            ("🎨 Remove Background", self.remove_background),
            ("📊 Digitalize Lead", self.digitalize_lead)
        ]
        
        for text, handler in buttons:
            btn = QPushButton(text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #34495E;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px;
                    font-size: 14px;
                    text-align: left;
                }
                QPushButton:hover {
                    background-color: #3498DB;
                }
                QPushButton:pressed {
                    background-color: #2980B9;
                }
            """)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(handler)
            layout.addWidget(btn)
        
        layout.addStretch()

    def go_back_to_main(self):
        """Return to main page"""
        if isinstance(self.main_window, QMainWindow):
            self.main_window.stacked_widget.setCurrentIndex(0)
    
    def update_display(self):
        if img is not None:
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            height, width = img_rgb.shape[:2]
            bytes_per_line = 3 * width
            q_img = QImage(img_rgb.data, width, height, bytes_per_line, 
                         QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            
            # Draw rectangles with improved style
            for rect in rectangles:
                x1, y1, x2, y2, name = rect
                pen = QPen(QColor("#3498DB"), 2)
                if rect == selected_rectangle:
                    pen.setColor(QColor("#E74C3C"))
                    # Add selection highlight
                    highlight = self.scene.addRect(x1, y1, x2-x1, y2-y1, 
                                                 QPen(Qt.NoPen),
                                                 QBrush(QColor(231, 76, 60, 50)))
                rect_item = self.scene.addRect(x1, y1, x2-x1, y2-y1, pen)
                
                # Add text label
                text = self.scene.addText(name)
                text.setDefaultTextColor(QColor("#2C3E50"))
                text.setPos(x1, y1 - 20)
            
            # Fit view while maintaining aspect ratio
            self.graphics_view.fitInView(
                self.scene.sceneRect(),
                Qt.KeepAspectRatio
            )
    
    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open ECG Image", "", 
            "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff)")
        if file_path:
            global img, opened_image_path, image_loaded, img_original_size, img_resized_size
            opened_image_path = file_path
            img = cv2.imread(file_path, cv2.IMREAD_COLOR)
            if img is not None:
                # Store original size
                img_original_size = (img.shape[1], img.shape[0])  # width, height
                
                # Resize image while maintaining aspect ratio
                height, width = img.shape[:2]
                aspect_ratio = width / height
                new_width = 1260
                new_height = int(new_width / aspect_ratio)
                img = cv2.resize(img, (new_width, new_height))
                img_resized_size = (new_width, new_height)
                
                # Display image
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                bytes_per_line = 3 * new_width
                q_img = QImage(img_rgb.data, new_width, new_height, bytes_per_line, 
                             QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.scene.clear()
                self.scene.addPixmap(pixmap)
                self.graphics_view.setScene(self.scene)
                self.graphics_view.fitInView(
                    self.scene.sceneRect(), 
                    Qt.KeepAspectRatio
                )
                image_loaded = True
            else:
                QMessageBox.critical(self, "Error", "Failed to load image")
    
    def delete_selected(self):
        global selected_rectangle, rectangles
        if selected_rectangle and selected_rectangle in rectangles:
            rectangles.remove(selected_rectangle)
            selected_rectangle = None
            self.update_display()
    
    def save_all_areas(self):
        """Save all rectangle areas as separate images."""
        if not rectangles or img is None:
            QMessageBox.warning(self, "Warning", "No rectangles to save!")
            return
            
        try:
            # Ask user for save directory
            save_dir = QFileDialog.getExistingDirectory(self, "Select Directory to Save Images")
            if not save_dir:
                return
                
            for rect in rectangles:
                x1, y1, x2, y2, name = rect
                
                # Convert coordinates to image space
                x1_resized = int(x1 * img_resized_size[0] / img_original_size[1])
                y1_resized = int(y1 * img_resized_size[1] / img_original_size[0])
                x2_resized = int(x2 * img_resized_size[0] / img_original_size[1])
                y2_resized = int(y2 * img_resized_size[1] / img_original_size[0])
                
                # Extract the rectangle area from the image
                sub_image = img[y1_resized:y2_resized, x1_resized:x2_resized]
                
                # Create filename with rectangle name
                filename = os.path.join(save_dir, f"{name}.png")
                
                # If file exists, add number to filename
                counter = 1
                while os.path.exists(filename):
                    filename = os.path.join(save_dir, f"{name}_{counter}.png")
                    counter += 1
                
                # Save the image
                cv2.imwrite(filename, sub_image)
            
            QMessageBox.information(self, "Success", f"All {len(rectangles)} areas saved successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save images: {str(e)}")
    
    def remove_background(self):
        if not opened_image_path:
            return
        try:
            global img
            # Convert the image to HSV color space
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Display HSV image in the application
            hsv_rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            height, width = hsv_rgb.shape[:2]
            bytes_per_line = 3 * width
            q_img = QImage(hsv_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.graphics_view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
            
            # Show message for HSV view
            QMessageBox.information(self, "Processing", "Showing HSV image. Click OK to continue with background removal.")

            # Define the range for the black color in HSV
            lower_black = np.array([0, 0, 0])    # Lower bound for black color
            upper_black = np.array([180, 255, 220])  # Upper bound for black color

            # Create a mask for the black color
            mask_black = cv2.inRange(hsv, lower_black, upper_black)

            # Create a white background
            white_background = np.full_like(img, 255)  # 255 is white for all channels

            # Invert the black mask to create a mask for non-black areas
            mask_inv = cv2.bitwise_not(mask_black)

            # Keep black areas from the image
            black_on_white = cv2.bitwise_and(img, img, mask=mask_black)

            # Make black areas more black (0)
            black_on_white[mask_black == 255] = 0  # Set black areas to 0 (pure black)

            # Apply white where it's not black
            non_black_on_white = cv2.bitwise_and(white_background, white_background, mask=mask_inv)

            # Combine the black areas with the white background
            preprocessed_img = cv2.add(black_on_white, non_black_on_white)

            # Display preprocessed image in the application
            preprocessed_rgb = cv2.cvtColor(preprocessed_img, cv2.COLOR_BGR2RGB)
            height, width = preprocessed_rgb.shape[:2]
            bytes_per_line = 3 * width
            q_img = QImage(preprocessed_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            self.scene.clear()
            self.scene.addPixmap(pixmap)
            self.graphics_view.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

            # Update the global image with the preprocessed result
            img = preprocessed_img
            
            # Save processed image
            new_path = opened_image_path.rsplit('.', 1)[0] + "_nobg.png"
            cv2.imwrite(new_path, preprocessed_img)
            
            # Redraw rectangles
            self.update_display()
            
            QMessageBox.information(self, "Success", "Background removed successfully!")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to remove background: {str(e)}")
    
    def digitalize_lead(self):
        if not rectangles:
            QMessageBox.warning(self, "Warning", "No rectangles drawn!")
            return
        dialog = DigitalizeDialog(self)
        dialog.exec_()

        # Step 2: Digitalize the signal
        # Convert the preprocessed image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Threshold the image to get a binary image (black signal on white background)
        _, binary = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY_INV)

        # Get the dimensions of the image
        height, width = binary.shape

        # Define the signal scaling factors based on your image size or expected signal range
        max_amplitude = 1  # Maximum amplitude of the ECG signal (adjust as needed)
        min_amplitude = -1  # Minimum amplitude of the ECG signal (adjust as needed)
        time_scale = 0.01  # Time per pixel in seconds (adjust according to image resolution)

        # Arrays to store the digitalized x and y values
        signal_x = []
        signal_y = []

        # Iterate over each column to find the middle y-coordinate of the signal
        for x in range(binary.shape[1]):  # Iterate over each column (x-axis)
            column = binary[:, x]  # Get the column
            # Find all the white pixels in the column
            y_indices = np.where(column == 255)[0]
            if len(y_indices) > 0:  # Check if there are any white pixels
                # Calculate the middle pixel
                y = (y_indices[0] + y_indices[-1]) // 2
                # Map the pixel coordinates to the actual ECG values
                # Normalize the y-coordinate to match the amplitude range
                normalized_y = max_amplitude - (max_amplitude - min_amplitude) * (y / height)

                # Map the x-coordinate to time (assuming a fixed time scale for now)
                time = x * time_scale

                signal_x.append(time)
                signal_y.append(normalized_y)

        # Save the digitalized signal as a CSV file
        with open('digitalized_signal.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Time (s)', 'Amplitude'])  # Column headers
            for time, amplitude in zip(signal_x, signal_y):
                writer.writerow([time, amplitude])

        print("Digitalized signal saved to 'digitalized_signal.csv'")

        # Plot the original image with the digitalized signal overlaid
        plt.figure(figsize=(width / 100, height / 100))
        plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        plt.plot([x / time_scale for x in signal_x],
                 [(1 - (y - min_amplitude) / (max_amplitude - min_amplitude)) * height for y in signal_y],
                 color='red', linewidth=1)
        plt.axis('off')
        print("Preprocessed Image with Digitalized Signal")
        plt.show()

        # Plot only the digitalized signal
        plt.figure(figsize=(10, 5))
        plt.plot(signal_x, signal_y, color='black')
        print("Digitalized ECG Signal")
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.grid(True)
        plt.show()

    def reset_workspace(self):
        """Reset the workspace to its original state."""
        if not opened_image_path:
            return
            
        try:
            global img, rectangles, selected_rectangle
            
            # Clear all rectangles
            rectangles = []
            selected_rectangle = None
            
            # Reload original image
            img = cv2.imread(opened_image_path, cv2.IMREAD_COLOR)
            if img is not None:
                # Resize image while maintaining aspect ratio
                height, width = img.shape[:2]
                aspect_ratio = width / height
                new_width = 1260
                new_height = int(new_width / aspect_ratio)
                img = cv2.resize(img, (new_width, new_height))
                
                # Display image
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                bytes_per_line = 3 * new_width
                q_img = QImage(img_rgb.data, new_width, new_height, bytes_per_line, 
                             QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.scene.clear()
                self.scene.addPixmap(pixmap)
                self.graphics_view.fitInView(
                    self.scene.sceneRect(), 
                    Qt.KeepAspectRatio
                )
                
                # Show success message
                QMessageBox.information(self, "Success", "Workspace has been reset to original state.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to reset workspace: {str(e)}")

    def add_to_history(self):
        """Add current state to history."""
        global rectangle_history, current_history_index
        # Remove any future history if we're not at the end
        rectangle_history = rectangle_history[:current_history_index + 1]
        # Add current state
        rectangle_history.append(rectangles.copy())
        current_history_index = len(rectangle_history) - 1

    def undo_action(self):
        """Undo the last action."""
        global rectangles, current_history_index
        if current_history_index > 0:
            current_history_index -= 1
            rectangles = rectangle_history[current_history_index].copy()
            self.update_display()

    def redo_action(self):
        """Redo the last undone action."""
        global rectangles, current_history_index
        if current_history_index < len(rectangle_history) - 1:
            current_history_index += 1
            rectangles = rectangle_history[current_history_index].copy()
            self.update_display()

    def eventFilter(self, obj, event):
        if obj == self.graphics_view.viewport() and image_loaded:
            if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
                scene_pos = self.graphics_view.mapToScene(event.pos())
                # Check if clicked on existing rectangle
                for rect in rectangles:
                    x1, y1, x2, y2, name = rect
                    if (x1 <= scene_pos.x() <= x2 and y1 <= scene_pos.y() <= y2):
                        # Delete the rectangle
                        rectangles.remove(rect)
                        self.add_to_history()
                        self.update_display()
                        return True
                
                # If not clicked on existing rectangle, start drawing new one
                self.start_pos = scene_pos
                self.drawing = True
                if self.current_rect:
                    self.scene.removeItem(self.current_rect)
                self.current_rect = self.scene.addRect(QRectF(self.start_pos, self.start_pos),
                                                     QPen(QColor("#3498DB"), 2))
                return True
                
            elif event.type() == event.MouseMove and self.drawing:
                if self.current_rect:
                    end_pos = self.graphics_view.mapToScene(event.pos())
                    rect = QRectF(self.start_pos, end_pos).normalized()
                    self.current_rect.setRect(rect)
                return True
                
            elif event.type() == event.MouseButtonRelease and event.button() == Qt.LeftButton and self.drawing:
                self.drawing = False
                if self.current_rect:
                    end_pos = self.graphics_view.mapToScene(event.pos())
                    rect = QRectF(self.start_pos, end_pos).normalized()
                    
                    # Get rectangle name from user
                    dialog = InputDialog(self, "Rectangle Name", "Enter name for the rectangle:")
                    if dialog.exec_() == QDialog.Accepted:
                        name = dialog.getValue()
                        if name:
                            rectangles.append((
                                rect.x(), rect.y(),
                                rect.x() + rect.width(),
                                rect.y() + rect.height(),
                                name
                            ))
                            self.add_to_history()
                            self.update_display()
                    else:
                        self.scene.removeItem(self.current_rect)
                    
                    self.current_rect = None
                    self.start_pos = None
                return True
                
        return super().eventFilter(obj, event)

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
        self.setMinimumSize(800, 600)  # Set minimum window size
        self._set_window_style()

        # Create stacked widget for multiple pages
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        # Create main page with responsive layout
        main_page = QWidget()
        main_layout = QVBoxLayout(main_page)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        self._create_content_area(main_layout)
        
        # Create ECG analysis page
        ecg_page = ECGAnalysisPage(self)
        
        # Add pages to stacked widget
        self.stacked_widget.addWidget(main_page)
        self.stacked_widget.addWidget(ecg_page)

        # Make window responsive
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def _set_window_style(self):
        """Sets the main window's background and style."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ECF0F1;
            }
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QToolTip {
                background-color: #2C3E50;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
                font-size: 13px;
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

    def _set_tools_panel_style(self, panel):
        """Sets the style for the tools panel."""
        panel.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-radius: 15px;
                padding: 20px;
                min-width: 300px;
                max-width: 300px;
            }
        """)

    def _add_tools_header(self, layout):
        """Adds the tools section header and description."""
        header_container = QFrame()
        header_container.setStyleSheet("background: transparent;")
        header_layout = QVBoxLayout(header_container)
        header_layout.setSpacing(10)
        
        tools_header = QLabel("Medical Tools")
        tools_header.setFont(QFont("Segoe UI", 24, QFont.Bold))
        tools_header.setStyleSheet("""
            color: white;
            padding-bottom: 10px;
            border-bottom: 2px solid #3498DB;
        """)
        header_layout.addWidget(tools_header)
        
        tools_desc = QLabel("Advanced ECG analysis and processing tools")
        tools_desc.setStyleSheet("color: #BDC3C7; font-size: 14px;")
        tools_desc.setWordWrap(True)
        header_layout.addWidget(tools_desc)
        
        layout.addWidget(header_container)

    def _add_tool_buttons(self, layout):
        """Adds the tool buttons to the panel."""
        button_style = """
            QPushButton {
                background-color: #34495E;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #3498DB;
            }
            QPushButton:pressed {
                background-color: #2980B9;
            }
        """
        
        # ECG Analysis button
        ecg_analysis_btn = QPushButton("🔬 ECG Analysis")
        ecg_analysis_btn.setStyleSheet(button_style)
        ecg_analysis_btn.setCursor(Qt.PointingHandCursor)
        ecg_analysis_btn.setMinimumHeight(80)
        ecg_analysis_btn.clicked.connect(self.show_ecg_analysis)
        layout.addWidget(ecg_analysis_btn)
        
        # Signal Processing button
        signal_proc_btn = QPushButton("📊 Signal Processing")
        signal_proc_btn.setStyleSheet(button_style)
        signal_proc_btn.setCursor(Qt.PointingHandCursor)
        signal_proc_btn.setMinimumHeight(80)
        layout.addWidget(signal_proc_btn)
        
        layout.addStretch()

    def _create_content_area(self, main_layout):
        """Creates the main content area with chat and tools panels."""
        content_widget = QWidget()
        content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_layout = QHBoxLayout(content_widget)
        content_layout.setSpacing(10)
        
        # Add chat interface with improved style and responsiveness
        chatbot = ChatbotWidget()
        chatbot.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        chatbot.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 15px;
            }
        """)
        content_layout.addWidget(chatbot, stretch=7)  # Increased ratio for chat

        # Add tools panel with fixed width
        tools_panel = self._create_tools_panel()
        content_layout.addWidget(tools_panel, stretch=3)  # Decreased ratio for tools
        
        main_layout.addWidget(content_widget)

    def _create_tools_panel(self):
        """Creates a responsive tools panel."""
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #2C3E50;
                border-radius: 15px;
                padding: 10px;
                min-width: 250px;
                max-width: 400px;
            }
        """)
        panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self._add_tools_header(layout)
        self._add_tool_buttons(layout)
        
        return panel

    def show_ecg_analysis(self):
        """Switch to the ECG analysis page"""
        self.stacked_widget.setCurrentIndex(1)
        # Update window title
        self.setWindowTitle('Medical AI Suite - ECG Analysis')

if __name__ == '__main__':
    # Initialize application
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 12))
    app.setStyle("Fusion")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())