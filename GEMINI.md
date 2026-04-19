# GEMINI.md

## Project Overview
This project, **solitare**, is a fully functional Solitaire game built with Python and Kivy. It features a polished drag-and-drop interface, high-legibility assets, and support for multiple languages.

## Project Type: Code Project
- **Language:** Python 3.x
- **UI Framework:** Kivy
- **Key Libraries:** `json`, `os`, `random`, `copy`, `time`, `sys`

## Building and Running
- **Install Dependencies:** `pip install -r requirements.txt`
- **Run the Game:** `python main.py`
- **Window Configuration:** Optimized for mobile-style aspect ratio (360x780).

## Current Features
- [x] **Core Solitaire Logic:** Standard Klondike rules implementation.
- [x] **Polished UI:** 
    - Dark green board theme.
    - High-legibility "Jumbo Index" card assets (`assets/cards/`).
    - Fanned waste pile rendering (shows top 2 cards).
    - Empty pile placeholders with light grey styling.
- [x] **Localization:** 
    - Support for English and Chinese (`assets/strings_zh.json`).
    - Automatic Chinese system font detection (`Microsoft YaHei`).
- [x] **Persistence & Logging:**
    - **Save/Load Game:** Manual save/load via UI buttons.
    - **Cross-Platform Storage:** Uses `App.user_data_dir` for Android/Windows compatibility.
    - **Auto-Cleanup:** Deletes save and log files older than 7 days on startup.
    - **Global Logging:** Redirects all `print` output to `game.log`.
- [x] **Smart Features:**
    - **Auto-Finish:** Automatically moves cards to foundations when the game is solveable (with user confirmation).
    - **Double-Tap to Auto-Move:** Quickly move cards to valid foundations or tableaus.
    - **Multi-Card Drag:** Move valid stacks between tableaus.
- [x] **Safety & UX:**
    - **Toast Notifications:** Animated feedback for save/load and errors.
    - "New Game" confirmation dialog to prevent accidental resets.
    - Undo functionality (up to 50 steps, persisted in save files).
    - UI blocking during dialogs and win screens.

## Development Conventions
- **Modular Architecture:**
    - `main.py`: Main layout orchestration and app entry point.
    - `logic.py`: Core game rules and state management (Klondike).
    - `storage.py`: Centralized file I/O, path management, and cleanup logic.
    - `logger.py`: System-wide output redirection to file.
    - `ui_widgets.py`: Reusable Kivy widgets (`CardWidget`, `PileTarget`).
    - `ui_dialogs.py`: `DialogMixin` for managing overlays and confirmation windows.
- **Data Persistence:** Game state is serialized to JSON. Undo history is included in the serialization.
- **Assets:** Card images are stored in `assets/cards/`.
- **Strings:** All UI text is externalized in JSON files for easy localization.

## TODO / Future Work
- [ ] Implement scoring system.
- [ ] Add sound effects and animations for card movements.
- [ ] Add more card back designs and board themes.
- [ ] Create a comprehensive test suite in `tests/`.
