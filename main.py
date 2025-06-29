#!/usr/bin/env python3
"""
Captain's Log - UEE Navy Interface
A Star Citizen-inspired logging system for UEE Navy operations.

Version: 1.0.0
Build Date: SET 2955.06.29.14.30 (June 29, 2025)
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QPalette
from ui.main_window import MainWindow
from core.database import LogDatabase


def create_splash_screen():
    """Create and show splash screen"""
    # Create a simple splash screen
    pixmap = QPixmap(400, 300)
    pixmap.fill(QColor(10, 10, 10))  # Dark background
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    # Draw title
    font = QFont("Consolas", 16, QFont.Weight.Bold)
    painter.setFont(font)
    painter.setPen(QColor(102, 179, 255))  # Light Blue
    painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, 
                    "CAPTAIN'S LOG\nUEE NAVY INTERFACE\n\nInitializing Systems...")
    
    # Draw border
    painter.setPen(QColor(77, 166, 255))  # Blue
    painter.drawRect(pixmap.rect().adjusted(5, 5, -5, -5))
    
    painter.end()
    
    splash = QSplashScreen(pixmap)
    splash.show()
    return splash


def setup_application_style(app):
    """Setup application-wide styling"""
    # Set application properties
    app.setApplicationName("Captain's Log")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("UEE Navy")
    app.setOrganizationDomain("navy.uee.gov")
    
    # Set dark palette as fallback
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(10, 10, 26))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(77, 166, 255))
    palette.setColor(QPalette.ColorRole.Base, QColor(26, 26, 46))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(15, 15, 30))
    palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(0, 0, 16))
    palette.setColor(QPalette.ColorRole.ToolTipText, QColor(77, 166, 255))
    palette.setColor(QPalette.ColorRole.Text, QColor(77, 166, 255))
    palette.setColor(QPalette.ColorRole.Button, QColor(26, 26, 46))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(77, 166, 255))
    palette.setColor(QPalette.ColorRole.BrightText, QColor(128, 204, 255))
    palette.setColor(QPalette.ColorRole.Link, QColor(102, 179, 255))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(102, 179, 255))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 16))
    
    app.setPalette(palette)


def check_system_requirements():
    """Check if system meets requirements"""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            return False, "Python 3.8 or higher is required"
        
        # Check PyQt6 installation
        from PyQt6.QtCore import QT_VERSION_STR
        if not QT_VERSION_STR:
            return False, "PyQt6 installation error"
        
        # Check write permissions for database
        try:
            test_file = "test_write_permission.tmp"
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
        except:
            return False, "No write permissions in current directory"
        
        return True, "System requirements met"
        
    except Exception as e:
        return False, f"System check failed: {str(e)}"


def initialize_database():
    """Initialize the application database"""
    try:
        db = LogDatabase()
        return True, "Database initialized successfully"
    except Exception as e:
        return False, f"Database initialization failed: {str(e)}"


def main():
    """Main application entry point"""
    print("="*60)
    print("CAPTAIN'S LOG - UEE NAVY INTERFACE")
    print("Version 1.0.0 | SET 2955.06.29.14.30")
    print("="*60)
    
    # Check system requirements
    print("Checking system requirements...")
    req_ok, req_msg = check_system_requirements()
    if not req_ok:
        print(f"❌ {req_msg}")
        input("Press Enter to exit...")
        sys.exit(1)
    print(f"✅ {req_msg}")
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Setup application styling
    setup_application_style(app)
    
    # Show splash screen
    print("Initializing user interface...")
    splash = create_splash_screen()
    app.processEvents()
    
    # Initialize database
    print("Initializing database systems...")
    splash.showMessage("Initializing Database...", Qt.AlignmentFlag.AlignBottom, QColor(0, 255, 0))
    app.processEvents()
    
    db_ok, db_msg = initialize_database()
    if not db_ok:
        splash.close()
        QMessageBox.critical(None, "Database Error", db_msg)
        sys.exit(1)
    print(f"✅ {db_msg}")
    
    # Create main window
    splash.showMessage("Loading Main Interface...", Qt.AlignmentFlag.AlignBottom, QColor(0, 255, 0))
    app.processEvents()
    
    try:
        main_window = MainWindow()
        
        # Close splash screen and show main window
        def show_main_window():
            splash.close()
            main_window.show()
            print("🚀 Captain's Log system online!")
            print("Ready for log entries, Captain. Welcome to the 'verse.")
        
        # Delay showing main window to let splash screen display
        QTimer.singleShot(2000, show_main_window)
        
        # Start the application event loop
        return app.exec()
        
    except Exception as e:
        splash.close()
        error_msg = f"Failed to start application:\n{str(e)}"
        print(f"❌ {error_msg}")
        QMessageBox.critical(None, "Startup Error", error_msg)
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        print("\nCaptain's Log system shutting down...")
        print("End of log. Computer, save and close. See you in the 'verse.")
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nEmergency shutdown initiated...")
        print("Captain's Log system offline.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Critical system error: {e}")
        print("Emergency protocols engaged. System offline.")
        sys.exit(1)
