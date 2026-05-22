import sys
import os

# Add the current directory to sys.path to allow imports from gui/
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from gui.main_window import MainWindow

def main():
    """Main entry point for the QR File Transfer System Pro."""
    try:
        app = MainWindow()
        app.mainloop()
    except Exception as e:
        print(f"Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
