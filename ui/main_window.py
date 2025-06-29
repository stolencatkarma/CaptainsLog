from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
                             QTabWidget, QPushButton, QLabel, QStatusBar,
                             QMenuBar, QMenu, QMessageBox, QGroupBox, QGridLayout,
                             QProgressBar, QSystemTrayIcon)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, pyqtSlot
from PyQt6.QtGui import QAction, QFont, QIcon, QPalette, QColor
import sys
import os
from datetime import datetime
from core.database import LogDatabase
from core.stardate import StardateCalculator, TimeUtils
from ui.log_entry import LogEntryDialog
from ui.log_viewer import LogViewer


class StatusUpdateThread(QThread):
    """Thread for updating status information without blocking UI"""
    status_updated = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.running = True
    
    def run(self):
        while self.running:
            try:
                stardate_info = StardateCalculator.get_stardate_info()
                self.status_updated.emit(stardate_info)
                self.msleep(1000)  # Update every second
            except Exception as e:
                print(f"Status update error: {e}")
                self.msleep(5000)  # Wait longer on error
    
    def stop(self):
        self.running = False
        self.wait()


class MainWindow(QMainWindow):
    """Main application window for Captain's Log"""
    
    def __init__(self):
        super().__init__()
        self.db = LogDatabase()
        self.status_thread = StatusUpdateThread()
        self.init_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.setup_connections()
        self.start_status_updates()
        self.apply_theme()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Captain's Log - UEE Navy Interface")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header section
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Main content area with tabs
        self.tab_widget = QTabWidget()
        
        # Log Entry tab
        self.log_entry_dialog = None  # Will be created when needed
        
        # Log Viewer tab
        self.log_viewer = LogViewer()
        self.tab_widget.addTab(self.log_viewer, "📋 Log Archive")
        
        # Status Dashboard tab
        status_dashboard = self.create_status_dashboard()
        self.tab_widget.addTab(status_dashboard, "📊 Status Dashboard")
        
        # Quick Actions tab
        quick_actions = self.create_quick_actions()
        self.tab_widget.addTab(quick_actions, "⚡ Quick Actions")
        
        main_layout.addWidget(self.tab_widget)
        
        # Set initial tab
        self.tab_widget.setCurrentIndex(0)
    
    def create_header(self):
        """Create the header section"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        
        # Main title
        title_label = QLabel("UEE NAVY - CAPTAIN'S LOG INTERFACE")
        title_label.setProperty("class", "title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        # Current time and stardate info
        time_layout = QHBoxLayout()
        
        self.stardate_display = QLabel("SET: Calculating...")
        self.stardate_display.setProperty("class", "stardate")
        time_layout.addWidget(self.stardate_display)
        
        time_layout.addStretch()
        
        self.earth_time_display = QLabel("Earth Time: Loading...")
        time_layout.addWidget(self.earth_time_display)
        
        header_layout.addLayout(time_layout)
        
        # Quick action buttons
        action_layout = QHBoxLayout()
        
        self.new_log_button = QPushButton("📝 New Log Entry")
        self.new_log_button.setProperty("class", "primary")
        action_layout.addWidget(self.new_log_button)
        
        self.emergency_log_button = QPushButton("🚨 Emergency Log")
        self.emergency_log_button.setProperty("class", "danger")
        action_layout.addWidget(self.emergency_log_button)
        
        action_layout.addStretch()
        
        self.system_status_label = QLabel("🟢 All Systems Operational")
        self.system_status_label.setProperty("class", "status")
        action_layout.addWidget(self.system_status_label)
        
        header_layout.addLayout(action_layout)
        
        return header_widget
    
    def create_status_dashboard(self):
        """Create status dashboard tab"""
        dashboard = QWidget()
        layout = QGridLayout(dashboard)
        
        # System Status
        status_group = QGroupBox("System Status")
        status_layout = QVBoxLayout(status_group)
        
        self.log_count_label = QLabel("Total Logs: Calculating...")
        status_layout.addWidget(self.log_count_label)
        
        self.database_status_label = QLabel("Database: Connected")
        status_layout.addWidget(self.database_status_label)
        
        self.uptime_label = QLabel("Session Uptime: 00:00:00")
        status_layout.addWidget(self.uptime_label)
        
        layout.addWidget(status_group, 0, 0)
        
        # Mission Parameters
        mission_group = QGroupBox("Mission Parameters")
        mission_layout = QVBoxLayout(mission_group)
        
        mission_layout.addWidget(QLabel("Current Mission: Deep Space Exploration"))
        mission_layout.addWidget(QLabel("Sector: Stanton System"))
        mission_layout.addWidget(QLabel("Ship Status: Green"))
        mission_layout.addWidget(QLabel("Crew Status: All Personnel Accounted"))
        
        layout.addWidget(mission_group, 0, 1)
        
        # Recent Activity
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_log = QLabel("Initializing activity monitor...")
        self.activity_log.setWordWrap(True)
        activity_layout.addWidget(self.activity_log)
        
        layout.addWidget(activity_group, 1, 0, 1, 2)
        
        return dashboard
    
    def create_quick_actions(self):
        """Create quick actions tab"""
        actions_widget = QWidget()
        layout = QGridLayout(actions_widget)
        
        # Pre-defined log templates
        templates_group = QGroupBox("Log Templates")
        templates_layout = QGridLayout(templates_group)
        
        template_buttons = [
            ("📊 Mission Report", "MISSION_REPORT"),
            ("👤 Personal Log", "PERSONAL_LOG"),
            ("🔧 System Status", "SYSTEM_STATUS"),
            ("🤝 Diplomatic Log", "DIPLOMATIC_LOG"),
            ("🔬 Scientific Log", "SCIENTIFIC_LOG"),
            ("🛡️ Security Alert", "SECURITY_ALERT"),
            ("🏥 Medical Log", "MEDICAL_LOG")
        ]
        
        for i, (text, log_type) in enumerate(template_buttons):
            button = QPushButton(text)
            button.clicked.connect(lambda checked, lt=log_type: self.create_template_log(lt))
            templates_layout.addWidget(button, i // 3, i % 3)
        
        layout.addWidget(templates_group, 0, 0)
        
        # Utilities
        utilities_group = QGroupBox("Utilities")
        utilities_layout = QVBoxLayout(utilities_group)
        
        export_button = QPushButton("📤 Export Logs")
        export_button.clicked.connect(self.export_logs)
        utilities_layout.addWidget(export_button)
        
        backup_button = QPushButton("💾 Backup Database")
        backup_button.clicked.connect(self.backup_database)
        utilities_layout.addWidget(backup_button)
        
        settings_button = QPushButton("⚙️ Settings")
        settings_button.clicked.connect(self.show_settings)
        utilities_layout.addWidget(settings_button)
        
        layout.addWidget(utilities_group, 0, 1)
        
        return actions_widget
    
    def setup_menu(self):
        """Setup the menu bar"""
        menubar = self.menuBar()
        if menubar is None:
            return
        
        # File menu
        file_menu = menubar.addMenu('&File')
        if file_menu is None:
            return
        
        new_log_action = QAction('&New Log Entry', self)
        new_log_action.setShortcut('Ctrl+N')
        new_log_action.triggered.connect(self.show_new_log_dialog)
        file_menu.addAction(new_log_action)
        
        file_menu.addSeparator()
        
        export_action = QAction('&Export Logs...', self)
        export_action.triggered.connect(self.export_logs)
        file_menu.addAction(export_action)
        
        backup_action = QAction('&Backup Database...', self)
        backup_action.triggered.connect(self.backup_database)
        file_menu.addAction(backup_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('&View')
        if view_menu is not None:
            refresh_action = QAction('&Refresh', self)
            refresh_action.setShortcut('F5')
            refresh_action.triggered.connect(self.refresh_data)
            view_menu.addAction(refresh_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        if help_menu is not None:
            about_action = QAction('&About', self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Setup the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_bar.showMessage("Captain's Log System Online")
        
        # Add permanent widgets to status bar
        self.connection_status = QLabel("🟢 Connected")
        self.status_bar.addPermanentWidget(self.connection_status)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.new_log_button.clicked.connect(self.show_new_log_dialog)
        self.emergency_log_button.clicked.connect(self.create_emergency_log)
        self.status_thread.status_updated.connect(self.update_status_displays)
        
        # Connect log viewer signals
        self.log_viewer.log_selected.connect(self.on_log_selected)
        self.log_viewer.edit_requested.connect(self.edit_log)
    
    def start_status_updates(self):
        """Start the status update thread"""
        self.status_thread.start()
        
        # Also set up a timer for session uptime
        self.session_start_time = datetime.now()
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        self.uptime_timer.start(1000)  # Update every second
    
    @pyqtSlot(dict)
    def update_status_displays(self, stardate_info):
        """Update status displays with current information"""
        self.stardate_display.setText(stardate_info['formatted_stardate'])
        self.earth_time_display.setText(f"Earth Time: {stardate_info['earth_date']}")
        
        # Update log count
        try:
            logs = self.db.get_logs(limit=1)  # Just to check connection
            total_logs = len(self.db.get_logs(limit=1000))  # Get a reasonable count
            self.log_count_label.setText(f"Total Logs: {total_logs}")
            self.database_status_label.setText("Database: Connected ✅")
            self.connection_status.setText("🟢 Connected")
        except Exception as e:
            self.database_status_label.setText("Database: Error ❌")
            self.connection_status.setText("🔴 Error")
    
    def update_uptime(self):
        """Update session uptime display"""
        uptime = datetime.now() - self.session_start_time
        hours, remainder = divmod(uptime.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        self.uptime_label.setText(f"Session Uptime: {uptime_str}")
    
    def show_new_log_dialog(self):
        """Show the new log entry dialog"""
        dialog = LogEntryDialog(self)
        dialog.log_saved.connect(self.on_log_saved)
        dialog.exec()
    
    def create_template_log(self, log_type):
        """Create a new log with a template"""
        dialog = LogEntryDialog(self)
        # Set the log type
        for i in range(dialog.log_type_combo.count()):
            if dialog.log_type_combo.itemText(i) == log_type:
                dialog.log_type_combo.setCurrentIndex(i)
                break
        
        # Set template content based on type
        templates = {
            'MISSION_REPORT': "Mission Status Report:\n\nObjective: \nProgress: \nChallenges: \nNext Steps: \n\nRecommendations: ",
            'PERSONAL_LOG': "Personal Log Entry:\n\nReflections on recent events...\n\n",
            'SYSTEM_STATUS': "System Status Report:\n\nPrimary Systems: \nSecondary Systems: \nMaintenance Required: \n\nTechnical Notes: ",
            'DIPLOMATIC_LOG': "Diplomatic Contact Report:\n\nSpecies/Entity: \nFirst Contact Protocol: \nCommunication Method: \nOutcome: \n\nCultural Notes: ",
            'SCIENTIFIC_LOG': "Scientific Discovery Log:\n\nPhenomenon Observed: \nHypothesis: \nTesting Results: \nConclusions: \n\nFurther Research: ",
            'SECURITY_ALERT': "Security Alert Report:\n\nThreat Level: \nNature of Threat: \nResponse Actions: \nResolution: \n\nRecommendations: ",
            'MEDICAL_LOG': "Medical Log Entry:\n\nPatient/Crew Status: \nSymptoms/Condition: \nTreatment: \nPrognosis: \n\nMedical Notes: "
        }
        
        if log_type in templates:
            dialog.content_edit.setPlainText(templates[log_type])
        
        dialog.log_saved.connect(self.on_log_saved)
        dialog.exec()
    
    def create_emergency_log(self):
        """Create an emergency log entry"""
        dialog = LogEntryDialog(self)
        
        # Set emergency defaults
        dialog.priority_combo.setCurrentIndex(4)  # Critical priority
        dialog.title_edit.setText("EMERGENCY LOG")
        dialog.content_edit.setPlainText("EMERGENCY SITUATION:\n\nNature of Emergency: \nImmediate Actions Taken: \nCurrent Status: \nAssistance Required: \n\nCommand Decision: ")
        
        # Set to mission report type
        for i in range(dialog.log_type_combo.count()):
            if dialog.log_type_combo.itemText(i) == 'MISSION_REPORT':
                dialog.log_type_combo.setCurrentIndex(i)
                break
        
        dialog.log_saved.connect(self.on_log_saved)
        dialog.exec()
    
    def on_log_saved(self, log_data):
        """Handle when a log is saved"""
        self.status_bar.showMessage(f"Log entry saved: {log_data['title']}", 3000)
        self.log_viewer.refresh_logs()
        
        # Update activity log
        activity_text = f"New log created: {log_data['title']} (Stardate {log_data['stardate']:.2f})"
        self.activity_log.setText(activity_text)
    
    def on_log_selected(self, log_data):
        """Handle log selection"""
        self.status_bar.showMessage(f"Selected: {log_data['title']}")
    
    def edit_log(self, log_data):
        """Edit an existing log"""
        dialog = LogEntryDialog(self, log_data)
        dialog.log_saved.connect(self.on_log_saved)
        dialog.exec()
    
    def export_logs(self):
        """Export logs to file"""
        QMessageBox.information(self, "Export", "Export functionality will be implemented in a future update.")
    
    def backup_database(self):
        """Backup the database"""
        QMessageBox.information(self, "Backup", "Database backup functionality will be implemented in a future update.")
    
    def show_settings(self):
        """Show settings dialog"""
        QMessageBox.information(self, "Settings", "Settings panel will be implemented in a future update.")
    
    def refresh_data(self):
        """Refresh all data displays"""
        self.log_viewer.refresh_logs()
        self.status_bar.showMessage("Data refreshed", 2000)
    
    def show_about(self):
        """Show about dialog"""
        about_text = """
        <h2>Captain's Log - UEE Navy Interface</h2>
        <p><b>Version:</b> 1.0.0</p>
        <p><b>Build Date:</b> SET 2955.06.29.14.30 (June 29, 2025)</p>
        <br>
        <p>A Star Citizen-inspired logging system for UEE Navy operations.</p>
        <p>Features secure log storage, SET calculations, and classification levels.</p>
        <br>
        <p><b>Developed for exploration and discovery in the 'verse.</b></p>
        <p><i>"Per aspera ad astra - Through hardships to the stars."</i></p>
        """
        
        QMessageBox.about(self, "About Captain's Log", about_text)
    
    def apply_theme(self):
        """Apply the futuristic theme"""
        try:
            with open('resources/styles/futuristic.qss', 'r') as f:
                self.setStyleSheet(f.read())
        except FileNotFoundError:
            print("Warning: Theme file not found. Using default theme.")
    
    def closeEvent(self, a0):
        """Handle application close"""
        self.status_thread.stop()
        if a0:
            a0.accept()
