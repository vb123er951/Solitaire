"""Redirects print output to a log file."""

import sys
import os
from storage import StorageManager

class LogManager:
    """Redirects stdout and stderr to a file in the user data directory."""
    
    _original_stdout = sys.stdout
    _original_stderr = sys.stderr
    _log_file = None

    @staticmethod
    def start():
        """Starts redirecting output to the log file."""
        log_path = StorageManager.get_log_path()
        try:
            # Ensure directory exists
            directory = os.path.dirname(log_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
                
            # Open in append mode
            LogManager._log_file = open(log_path, 'a', encoding='utf-8')
            sys.stdout = LogManager(LogManager._original_stdout, LogManager._log_file)
            sys.stderr = LogManager(LogManager._original_stderr, LogManager._log_file)
            print(f"\n--- Log started at {os.path.basename(log_path)} ---")
        except Exception as e:
            print(f"Failed to start LogManager: {e}")

    @staticmethod
    def stop():
        """Stops redirecting and closes the log file."""
        sys.stdout = LogManager._original_stdout
        sys.stderr = LogManager._original_stderr
        if LogManager._log_file:
            LogManager._log_file.close()
            LogManager._log_file = None

    def __init__(self, terminal, file):
        self.terminal = terminal
        self.file = file

    def write(self, message):
        self.terminal.write(message)
        self.file.write(message)
        self.file.flush() # Ensure it's written immediately

    def flush(self):
        self.terminal.flush()
        self.file.flush()
