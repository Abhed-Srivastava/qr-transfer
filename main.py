import sys
import os

# Add the current directory to sys.path to allow imports from gui/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import MainWindow

def main():
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"Failed to start GUI: {e}")
        print("Falling back to CLI...")
        # Add CLI fallback logic here if needed
        import argparse
        parser = argparse.ArgumentParser(description="QR File Transfer System Pro")
        # ... (CLI logic from previous version or extended)
        print("Please run with --help for CLI usage.")

if __name__ == "__main__":
    main()
