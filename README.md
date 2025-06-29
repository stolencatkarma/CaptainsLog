# Captain's Log - UEE Navy Interface

A Star Citizen-inspired PyQt6 application that mimics the function of a captain's log from the UEE Navy. Features a sleek blue-themed interface with comprehensive logging capabilities using Star Citizen's Standard Earth Time (SET) system.

## 🚀 Features

### Core Functionality
- **SET System**: Star Citizen's Standard Earth Time calculation and display (e.g., 2955.06.29.14.30)
- **Rich Log Entries**: Support for different log types (Mission Reports, Personal Logs, System Status, etc.)
- **Classification Levels**: UNCLASSIFIED, CLASSIFIED, and TOP_SECRET with encryption
- **Priority System**: 5-level priority system for log importance
- **Advanced Search**: Search logs by content, type, priority, and date
- **Secure Storage**: SQLite database with encryption for classified entries

### User Interface
- **Star Citizen Theme**: Dark blue interface with multiple shades of blue accents
- **Multiple Tabs**: Log Archive, Status Dashboard, and Quick Actions
- **Real-time Updates**: Live SET and system status updates
- **Log Templates**: Pre-defined templates for different log types
- **Emergency Logging**: Quick emergency log creation

### Log Types
- 📊 Mission Report
- 👤 Personal Log  
- 🔧 System Status
- 🤝 Diplomatic Log
- 🔬 Scientific Log
- 🛡️ Security Alert
- 🏥 Medical Log

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Windows, macOS, or Linux

### Setup Instructions

1. **Clone or Download** the project to your local machine

2. **Navigate to the project directory**:
   ```bash
   cd CaptainsLog
   ```

3. **Install Dependencies**:
   The application will automatically set up a virtual environment and install dependencies when first run.

4. **Run the Application**:
   ```bash
   python main.py
   ```

### Manual Installation (Alternative)

If you prefer to set up manually:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## 📖 Usage Guide

### Creating Log Entries

1. **New Log Entry**: Click "📝 New Log Entry" or use Ctrl+N
2. **Select Log Type**: Choose from predefined categories
3. **Set Priority**: 1 (Routine) to 5 (Critical)
4. **Classification**: Choose security level
5. **Enter Content**: Use the rich text editor
6. **Save**: Log is automatically timestamped with stardate

### Emergency Logs

- Click "🚨 Emergency Log" for immediate critical entries
- Pre-configured with high priority and emergency template

### Viewing Logs

- **Log Archive Tab**: Browse all entries
- **Search & Filter**: Use text search and filters
- **Content Viewer**: Full log details and content
- **Edit/Delete**: Modify or remove entries

### Security Features

- **Classified Logs**: Automatically encrypted in database
- **Access Levels**: Visual indicators for classification
- **Secure Storage**: Encrypted sensitive content

## 📁 Project Structure

```
CaptainsLog/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── ui/                     # User interface modules
│   ├── __init__.py
│   ├── main_window.py      # Main application window
│   ├── log_entry.py        # Log entry dialog
│   └── log_viewer.py       # Log browsing interface
├── core/                   # Core functionality
│   ├── __init__.py
│   ├── database.py         # Database operations
│   └── stardate.py         # Stardate calculations
└── resources/              # Application resources
    ├── styles/
    │   └── futuristic.qss  # Application theme
    ├── sounds/             # Sound effects (future)
    └── icons/              # Icons (future)
```

## 🎨 Customization

### Theme Modification
Edit `resources/styles/futuristic.qss` to customize the appearance:
- Colors: Modify hex values for different themes
- Fonts: Change font families and sizes
- Effects: Adjust borders, shadows, and animations

### SET System
The SET (Standard Earth Time) system can be modified in `core/stardate.py`:
- Star Citizen year offset (currently +930 years)
- Calculation algorithms
- Display formats

## 🔧 Technical Details

### Database Schema
- **logs**: Main log entries table
- **log_types**: Predefined log categories
- Encryption for classified content using Fernet symmetric encryption

### Dependencies
- **PyQt6**: GUI framework
- **cryptography**: Encryption for classified logs
- **python-dateutil**: Enhanced date/time handling

### System Requirements
- Python 3.8+
- 50MB disk space
- 512MB RAM minimum
- Write permissions in application directory

## 🚨 Troubleshooting

### Common Issues

**Application won't start**:
- Check Python version (3.8+ required)
- Ensure write permissions in directory
- Verify PyQt6 installation

**Database errors**:
- Check disk space
- Verify write permissions
- Delete `captains_log.db` to reset (loses data)

**Theme not loading**:
- Verify `resources/styles/futuristic.qss` exists
- Check file permissions

### Debug Mode
Run with debug output:
```bash
python main.py --debug
```

## 🔮 Future Enhancements

- Voice-to-text log entry
- Export to PDF/HTML
- Network sync capabilities
- Sound effects and animations
- Custom log type creation
- Advanced reporting features
- Multi-language support

## 📜 License

This project is created for educational and entertainment purposes. 

## 🖖 Credits

Inspired by Star Citizen's UEE Navy interface design and the immersive universe of the 'verse.

---

**"Captain's Log, SET 2955.06.29.14.30. Today we begin a new mission of digital exploration in the 'verse..."**

*See you in the 'verse.* �
