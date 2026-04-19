# Solitaire (Klondike)

A fully functional, polished Solitaire (Klondike) game built with **Python** and the **Kivy** framework. Designed with a focus on high legibility, smooth mobile-friendly interactions, and cross-platform compatibility (Windows & Android).

## Features

- **Core Gameplay:** Full implementation of standard Klondike Solitaire rules.
- **Modern UI:**
  - Dark green casino-style board.
  - **High-Legibility Assets:** Uses "Jumbo Index" card designs for better visibility on mobile screens.
- **Smart Interactions:**
  - **Drag-and-Drop:** Intuitive card movement with multi-card stack support.
  - **Double-Tap to Auto-Move:** Quickly send cards to valid foundations or tableaus.
  - **Auto-Finish:** Automatically completes the game when all cards are face-up and the stock is empty.
- **Localization:** Full support for **English** and **Chinese** (Traditional) with automatic font detection.
- **Persistence:**
  - **Save/Load:** Manually save your progress and resume later.
  - **Undo System:** Supports up to 50 steps of move history.
  - **Auto-Cleanup:** Automatically manages old save and log files.
- **Interactive Feedback:** Animated toast notifications and clear confirmation dialogs.

## Image Resources

The card assets used in this project are located in `assets/cards/`. 
- **Card Set:** "Jumbo Index" high-legibility playing cards. Referenced from [SVGCards](https://github.com/saulspatz/SVGCards)
- **Custom Assets:** Includes a custom game icon (`assets/icon.png`) and card back design (`assets/cards/back.png`).

There are another set of cards located in `assets/cards/`. It was download from internet

## Text Font Resources

The text Font `Noto Sans TC Variable Font` is download from [Google Font](https://fonts.google.com/noto/specimen/Noto+Sans+TC?preview.script=Hant)

## Installation & Running

### Prerequisites
- Python 3.8+
- Kivy 2.3.0+

### Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## Project Structure

The project follows a modular mixin-based architecture for better maintainability:
- `main.py`: Entry point and main layout orchestration.
- `logic.py`: Core Klondike rules and state management.
- `ui_mixins.py`: Shared UI behaviors (styling, toasts, actions).
- `ui_dialogs.py`: Confirmation and win-screen dialog overlays.
- `ui_widgets.py`: Specialized Kivy widgets for cards and piles.
- `storage.py`: Centralized save/load and file management logic.
- `logger.py`: System-wide log redirection.

## License
This project is for educational/personal use. Please refer to the `assets/cards/` directory for specific license terms regarding the image assets.
