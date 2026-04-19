"""Handles all file-related operations for the Solitaire game."""

import os
import json
import time

class StorageManager:
    """Manages game state persistence and file cleanup."""

    @staticmethod
    def get_save_path():
        """Returns the platform-specific path for the save game file."""
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app and app.user_data_dir:
                return os.path.join(app.user_data_dir, 'savegame.json')
        except (ImportError, Exception):
            pass
        return 'savegame.json'

    @staticmethod
    def get_log_path():
        """Returns the platform-specific path for the log file."""
        try:
            from kivy.app import App
            app = App.get_running_app()
            if app and app.user_data_dir:
                return os.path.join(app.user_data_dir, 'game.log')
        except (ImportError, Exception):
            pass
        return 'game.log'

    @staticmethod
    def save_game(game_state):
        """Serializes and saves the game state to a file."""
        filename = StorageManager.get_save_path()
        try:
            directory = os.path.dirname(filename)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(game_state.to_dict(), f, indent=4)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False

    @staticmethod
    def load_game(game_state):
        """Loads and deserializes the game state from a file."""
        filename = StorageManager.get_save_path()
        if not os.path.exists(filename):
            return False
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            game_state.from_dict(data)
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False

    @staticmethod
    def cleanup_old_files(days=7):
        """Deletes save and log files if they are older than the specified number of days."""
        paths = [StorageManager.get_save_path(), StorageManager.get_log_path()]
        for path in paths:
            if os.path.exists(path):
                try:
                    file_time = os.path.getmtime(path)
                    current_time = time.time()
                    limit_seconds = days * 24 * 60 * 60
                    
                    if current_time - file_time > limit_seconds:
                        os.remove(path)
                        print(f"Cleaned up old file (older than {days} days): {path}")
                except Exception as e:
                    # Can't easily print if logger is active, but we'll try
                    pass
