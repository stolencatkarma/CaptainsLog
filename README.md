# Captain's Log - UEE Navy Interface

A futuristic logbook application inspired by Star Citizen, designed for immersive roleplay and efficient log management for UEE Navy personnel.

## Features
- **Futuristic UI**: Modern gradients, card-based layouts, and Font Awesome icons for a sci-fi look.
- **Log Entry System**: Create, edit, and manage log entries with stardate and earth date tracking.
- **Priority & Classification**: Assign priority and classification levels to each log.
- **Search & Filter**: Quickly find logs by date, type, or keywords.
- **Data Security**: Optional encryption for classified and top-secret logs.

## Screenshots
![screenshot](resources/screenshots/main_ui.png)

## Installation
1. Clone this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. (Optional) Download `fontawesome-webfont.ttf` and place it in `resources/fonts/` for icon support.
4. Run the app:
   ```bash
   python main.py
   ```

## Usage
- Click **New Log** to create a new entry.
- Fill in the details, assign priority/classification, and save.
- Use the log viewer to browse, search, and filter entries.

## Development
- UI styles are in `resources/styles/futuristic.qss`.
- Main logic in `ui/` and `core/` folders.

## Credits
- Inspired by Star Citizen and sci-fi UIs.
- Icons by [Font Awesome](https://fontawesome.com/).

---
*For roleplay and personal use. Not affiliated with CIG or Star Citizen.*
