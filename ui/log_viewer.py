from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget,
                             QListWidgetItem, QTextEdit, QLineEdit, QPushButton,
                             QComboBox, QLabel, QGroupBox, QSplitter, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCharFormat, QColor
from datetime import datetime
from core.database import LogDatabase
from core.stardate import StardateCalculator


class LogListItem(QListWidgetItem):
    """Custom list item for displaying log entries"""
    
    def __init__(self, log_data):
        super().__init__()
        self.log_data = log_data
        self.update_display()
    
    def update_display(self):
        """Update the display text for this item"""
        log = self.log_data
        
        # Format the display text
        priority_indicator = "🔴" if log['priority'] >= 4 else "🟡" if log['priority'] >= 3 else "🟢"
        classification_indicator = "🔒" if log['classification'] != 'UNCLASSIFIED' else ""
        
        display_text = f"{priority_indicator} {classification_indicator}\n"
        display_text += f"SET {log['stardate']} | {log['log_type']}\n"
        display_text += f"{log['title']}\n"
        display_text += f"Earth Date: {log['earth_date']}"
        
        self.setText(display_text)
        
        # Set tooltip with full info
        tooltip = f"Priority: {log['priority']}\n"
        tooltip += f"Classification: {log['classification']}\n"
        tooltip += f"Created: {log['created_at']}\n"
        tooltip += f"ID: {log['id']}"
        self.setToolTip(tooltip)


class LogViewer(QWidget):
    """Widget for viewing and managing log entries"""
    
    log_selected = pyqtSignal(dict)
    edit_requested = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = LogDatabase()
        self.current_logs = []
        self.selected_log = None
        self.init_ui()
        self.setup_connections()
        self.load_logs()
    
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("LOG ARCHIVE ACCESS")
        header_label.setProperty("class", "title")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Search and filter section
        filter_group = QGroupBox("Search & Filter")
        filter_layout = QVBoxLayout(filter_group)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search logs by title or content...")
        search_layout.addWidget(self.search_edit)
        
        self.search_button = QPushButton("Search")
        search_layout.addWidget(self.search_button)
        
        self.clear_search_button = QPushButton("Clear")
        search_layout.addWidget(self.clear_search_button)
        
        filter_layout.addLayout(search_layout)
        
        # Filter options
        filter_options_layout = QHBoxLayout()
        
        filter_options_layout.addWidget(QLabel("Filter by Type:"))
        self.type_filter_combo = QComboBox()
        self.type_filter_combo.addItem("All Types", None)
        self.populate_type_filter()
        filter_options_layout.addWidget(self.type_filter_combo)
        
        filter_options_layout.addWidget(QLabel("Priority:"))
        self.priority_filter_combo = QComboBox()
        self.priority_filter_combo.addItems([
            "All Priorities",
            "Priority 1+",
            "Priority 2+", 
            "Priority 3+",
            "Priority 4+",
            "Priority 5 Only"
        ])
        filter_options_layout.addWidget(self.priority_filter_combo)
        
        filter_options_layout.addStretch()
        
        self.refresh_button = QPushButton("Refresh")
        filter_options_layout.addWidget(self.refresh_button)
        
        filter_layout.addLayout(filter_options_layout)
        layout.addWidget(filter_group)
        
        # Main content area
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Log list
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        list_header = QLabel("Log Entries")
        list_header.setProperty("class", "stardate")
        list_layout.addWidget(list_header)
        
        self.log_list = QListWidget()
        self.log_list.setAlternatingRowColors(True)
        list_layout.addWidget(self.log_list)
        
        # List controls
        list_controls = QHBoxLayout()
        self.edit_button = QPushButton("Edit Log")
        self.delete_button = QPushButton("Delete Log")
        self.delete_button.setProperty("class", "danger")
        
        list_controls.addWidget(self.edit_button)
        list_controls.addWidget(self.delete_button)
        list_controls.addStretch()
        
        list_layout.addLayout(list_controls)
        
        splitter.addWidget(list_widget)
        
        # Right side - Log content viewer
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        content_header = QLabel("Log Content")
        content_header.setProperty("class", "stardate")
        content_layout.addWidget(content_header)
        
        # Log details
        self.details_label = QLabel("Select a log entry to view details")
        self.details_label.setProperty("class", "status")
        self.details_label.setWordWrap(True)
        content_layout.addWidget(self.details_label)
        
        # Content display
        self.content_display = QTextEdit()
        self.content_display.setReadOnly(True)
        self.content_display.setPlaceholderText("Log content will appear here...")
        content_layout.addWidget(self.content_display)
        
        splitter.addWidget(content_widget)
        
        # Set splitter proportions
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setProperty("class", "status")
        layout.addWidget(self.status_label)
    
    def populate_type_filter(self):
        """Populate the type filter combo box"""
        log_types = self.db.get_log_types()
        for log_type in log_types:
            self.type_filter_combo.addItem(log_type['name'], log_type['name'])
    
    def setup_connections(self):
        """Setup signal connections"""
        self.search_button.clicked.connect(self.search_logs)
        self.clear_search_button.clicked.connect(self.clear_search)
        self.search_edit.returnPressed.connect(self.search_logs)
        self.type_filter_combo.currentTextChanged.connect(self.filter_logs)
        self.priority_filter_combo.currentTextChanged.connect(self.filter_logs)
        self.refresh_button.clicked.connect(self.load_logs)
        self.log_list.itemClicked.connect(self.on_log_selected)
        self.edit_button.clicked.connect(self.edit_selected_log)
        self.delete_button.clicked.connect(self.delete_selected_log)
    
    def load_logs(self):
        """Load logs from database"""
        try:
            self.current_logs = self.db.get_logs(limit=100)
            self.update_log_list()
            self.status_label.setText(f"Loaded {len(self.current_logs)} log entries")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load logs:\n{str(e)}")
            self.status_label.setText("Error loading logs")
    
    def update_log_list(self):
        """Update the log list display"""
        self.log_list.clear()
        
        for log in self.current_logs:
            item = LogListItem(log)
            self.log_list.addItem(item)
        
        # Update button states
        self.edit_button.setEnabled(False)
        self.delete_button.setEnabled(False)
        
        # Clear content display
        self.content_display.clear()
        self.details_label.setText("Select a log entry to view details")
    
    def search_logs(self):
        """Search logs based on search term"""
        search_term = self.search_edit.text().strip()
        
        if not search_term:
            self.load_logs()
            return
        
        try:
            self.current_logs = self.db.search_logs(search_term)
            self.update_log_list()
            self.status_label.setText(f"Found {len(self.current_logs)} matching logs")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Search failed:\n{str(e)}")
    
    def clear_search(self):
        """Clear search and reload all logs"""
        self.search_edit.clear()
        self.type_filter_combo.setCurrentIndex(0)
        self.priority_filter_combo.setCurrentIndex(0)
        self.load_logs()
    
    def filter_logs(self):
        """Filter logs based on selected criteria"""
        # Get filter criteria
        type_filter = self.type_filter_combo.currentData()
        priority_text = self.priority_filter_combo.currentText()
        
        # Start with all logs or search results
        if self.search_edit.text().strip():
            filtered_logs = self.db.search_logs(self.search_edit.text().strip())
        else:
            filtered_logs = self.db.get_logs(limit=100)
        
        # Apply type filter
        if type_filter:
            filtered_logs = [log for log in filtered_logs if log['log_type'] == type_filter]
        
        # Apply priority filter
        if priority_text != "All Priorities":
            if priority_text == "Priority 5 Only":
                filtered_logs = [log for log in filtered_logs if log['priority'] == 5]
            else:
                min_priority = int(priority_text.split()[1].replace('+', ''))
                filtered_logs = [log for log in filtered_logs if log['priority'] >= min_priority]
        
        self.current_logs = filtered_logs
        self.update_log_list()
        self.status_label.setText(f"Filtered to {len(self.current_logs)} logs")
    
    def on_log_selected(self, item):
        """Handle log selection"""
        if isinstance(item, LogListItem):
            self.selected_log = item.log_data
            self.display_log_content(self.selected_log)
            self.edit_button.setEnabled(True)
            self.delete_button.setEnabled(True)
            self.log_selected.emit(self.selected_log)
    
    def display_log_content(self, log_data):
        """Display the selected log's content"""
        # Update details label
        details = f"SET {log_data['stardate']} | {log_data['log_type']} | "
        details += f"Priority {log_data['priority']} | {log_data['classification']}"
        self.details_label.setText(details)
        
        # Format and display content
        content = f"TITLE: {log_data['title']}\n"
        content += f"SET: {log_data['stardate']}\n"
        content += f"EARTH DATE: {log_data['earth_date']}\n"
        content += f"LOG TYPE: {log_data['log_type']}\n"
        content += f"PRIORITY: {log_data['priority']}\n"
        content += f"CLASSIFICATION: {log_data['classification']}\n"
        content += f"CREATED: {log_data['created_at']}\n"
        content += "\n" + "="*50 + "\n\n"
        content += log_data['content']
        
        self.content_display.setPlainText(content)
        
        # Apply formatting based on classification
        if log_data['classification'] == 'TOP_SECRET':
            self.content_display.setStyleSheet("background-color: #2a0000; color: #ff0000;")
        elif log_data['classification'] == 'CLASSIFIED':
            self.content_display.setStyleSheet("background-color: #2a2a00; color: #ffff00;")
        else:
            self.content_display.setStyleSheet("")
    
    def edit_selected_log(self):
        """Edit the selected log"""
        if self.selected_log:
            self.edit_requested.emit(self.selected_log)
    
    def delete_selected_log(self):
        """Delete the selected log"""
        if not self.selected_log:
            return
        
        reply = QMessageBox.question(
            self, 
            "Delete Log Entry",
            f"Are you sure you want to delete this log entry?\n\n"
            f"Title: {self.selected_log['title']}\n"
            f"SET: {self.selected_log['stardate']}\n\n"
            f"This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = self.db.delete_log(self.selected_log['id'])
                if success:
                    self.status_label.setText("Log entry deleted successfully")
                    self.load_logs()  # Refresh the list
                else:
                    QMessageBox.warning(self, "Error", "Failed to delete log entry")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete log:\n{str(e)}")
    
    def refresh_logs(self):
        """Refresh the log list"""
        self.load_logs()
