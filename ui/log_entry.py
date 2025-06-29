from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                             QLineEdit, QTextEdit, QComboBox, QSpinBox,
                             QPushButton, QLabel, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from datetime import datetime
from core.stardate import StardateCalculator
from core.database import LogDatabase


class LogEntryDialog(QDialog):
    log_saved = pyqtSignal(dict)  # Signal emitted when a log is saved
    
    def __init__(self, parent=None, log_data=None):
        super().__init__(parent)
        self.log_data = log_data  # For editing existing logs
        self.db = LogDatabase()
        self.init_ui()
        self.setup_connections()
        
        if log_data:
            self.populate_fields(log_data)
        else:
            self.update_stardate()
    
    def init_ui(self):
        self.setWindowTitle("UEE Navy Log Entry")
        self.setModal(True)
        self.resize(800, 600)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("UEE NAVY LOG ENTRY")
        title_label.setProperty("class", "title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Stardate and Date info
        date_group = QGroupBox("Temporal Coordinates")
        date_layout = QFormLayout(date_group)
        
        self.stardate_label = QLabel()
        self.stardate_label.setProperty("class", "stardate")
        date_layout.addRow("Current SET:", self.stardate_label)
        
        self.earth_date_label = QLabel()
        date_layout.addRow("Earth Date:", self.earth_date_label)
        
        layout.addWidget(date_group)
        
        # Log entry form
        form_group = QGroupBox("Log Entry Details")
        form_layout = QFormLayout(form_group)
        
        # Log type
        self.log_type_combo = QComboBox()
        self.populate_log_types()
        form_layout.addRow("Log Type:", self.log_type_combo)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems([
            "1 - Routine",
            "2 - Standard", 
            "3 - Important",
            "4 - Urgent",
            "5 - Critical"
        ])
        self.priority_combo.setCurrentIndex(1)  # Default to Standard
        form_layout.addRow("Priority:", self.priority_combo)
        
        # Classification
        self.classification_combo = QComboBox()
        self.classification_combo.addItems([
            "UNCLASSIFIED",
            "CLASSIFIED",
            "TOP_SECRET"
        ])
        form_layout.addRow("Classification:", self.classification_combo)
        
        # Title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter log entry title...")
        form_layout.addRow("Title:", self.title_edit)
        
        layout.addWidget(form_group)
        
        # Content
        content_group = QGroupBox("Log Content")
        content_layout = QVBoxLayout(content_group)
        
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("Begin log entry...\n\nCommander's personal note: Remember to maintain proper stardate formatting and include all relevant mission details.")
        self.content_edit.setMinimumHeight(200)
        content_layout.addWidget(self.content_edit)
        
        layout.addWidget(content_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save Log Entry")
        self.save_button.setProperty("class", "primary")
        
        self.cancel_button = QPushButton("Cancel")
        
        self.clear_button = QPushButton("Clear All")
        self.clear_button.setProperty("class", "danger")
        
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setProperty("class", "status")
        layout.addWidget(self.status_label)
    
    def populate_log_types(self):
        """Populate log type combo box with available types"""
        log_types = self.db.get_log_types()
        for log_type in log_types:
            self.log_type_combo.addItem(log_type['name'], log_type)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.save_button.clicked.connect(self.save_log)
        self.cancel_button.clicked.connect(self.reject)
        self.clear_button.clicked.connect(self.clear_form)
        self.classification_combo.currentTextChanged.connect(self.on_classification_changed)
    
    def update_stardate(self):
        """Update stardate and date displays"""
        stardate_info = StardateCalculator.get_stardate_info()
        self.stardate_label.setText(stardate_info['formatted_stardate'])
        self.earth_date_label.setText(stardate_info['earth_date_long'])
    
    def on_classification_changed(self, classification):
        """Handle classification level changes"""
        if classification in ['CLASSIFIED', 'TOP_SECRET']:
            self.status_label.setText(f"⚠️ {classification} - Content will be encrypted")
            if classification == 'TOP_SECRET':
                self.status_label.setStyleSheet("color: #ff0000; font-weight: bold;")
            else:
                self.status_label.setStyleSheet("color: #ffff00; font-weight: bold;")
        else:
            self.status_label.setText("Standard log entry - No encryption")
            self.status_label.setStyleSheet("color: #00ff00;")
    
    def populate_fields(self, log_data):
        """Populate fields when editing an existing log"""
        # Find and set log type
        for i in range(self.log_type_combo.count()):
            if self.log_type_combo.itemText(i) == log_data['log_type']:
                self.log_type_combo.setCurrentIndex(i)
                break
        
        # Set priority
        self.priority_combo.setCurrentIndex(log_data['priority'] - 1)
        
        # Set classification
        classification_index = ['UNCLASSIFIED', 'CLASSIFIED', 'TOP_SECRET'].index(log_data['classification'])
        self.classification_combo.setCurrentIndex(classification_index)
        
        # Set title and content
        self.title_edit.setText(log_data['title'])
        self.content_edit.setPlainText(log_data['content'])
        
        # Update stardate display
        self.stardate_label.setText(f"SET {log_data['stardate']}")
        self.earth_date_label.setText(log_data['earth_date'])
    
    def clear_form(self):
        """Clear all form fields"""
        reply = QMessageBox.question(self, "Clear Form", 
                                   "Are you sure you want to clear all fields?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.title_edit.clear()
            self.content_edit.clear()
            self.log_type_combo.setCurrentIndex(0)
            self.priority_combo.setCurrentIndex(1)
            self.classification_combo.setCurrentIndex(0)
            self.update_stardate()
    
    def validate_form(self):
        """Validate form data before saving"""
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a title for the log entry.")
            self.title_edit.setFocus()
            return False
        
        if not self.content_edit.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter content for the log entry.")
            self.content_edit.setFocus()
            return False
        
        return True
    
    def save_log(self):
        """Save the log entry"""
        if not self.validate_form():
            return
        
        try:
            # Get current stardate and earth date
            stardate_info = StardateCalculator.get_stardate_info()
            
            # Prepare log data
            log_data = {
                'stardate': stardate_info['stardate'],
                'earth_date': stardate_info['earth_date'],
                'log_type': self.log_type_combo.currentText(),
                'priority': self.priority_combo.currentIndex() + 1,
                'classification': self.classification_combo.currentText(),
                'title': self.title_edit.text().strip(),
                'content': self.content_edit.toPlainText().strip()
            }
            
            # Save to database
            log_id = self.db.create_log_entry(**log_data)
            log_data['id'] = log_id
            
            # Show success message
            self.status_label.setText(f"✅ Log entry saved successfully (ID: {log_id})")
            self.status_label.setStyleSheet("color: #00ff00; font-weight: bold;")
            
            # Emit signal
            self.log_saved.emit(log_data)
            
            # Close dialog after a brief pause
            self.save_button.setText("Saved!")
            self.save_button.setEnabled(False)
            
            # Auto-close after 2 seconds or allow manual close
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, self.accept)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save log entry:\n{str(e)}")
    
    def get_log_data(self):
        """Return current form data as dictionary"""
        stardate_info = StardateCalculator.get_stardate_info()
        
        return {
            'stardate': stardate_info['stardate'],
            'earth_date': stardate_info['earth_date'],
            'log_type': self.log_type_combo.currentText(),
            'priority': self.priority_combo.currentIndex() + 1,
            'classification': self.classification_combo.currentText(),
            'title': self.title_edit.text().strip(),
            'content': self.content_edit.toPlainText().strip()
        }
