import PyInstaller.__main__
import os
import shutil

def build():
    print("Starting build process...")
    
    # Path to main script
    main_script = "main.py"
    
    # App name
    app_name = "QRTransferPro"
    
    # Paths to include (if any)
    # CustomTkinter needs its theme files sometimes, but usually it's handled.
    # We include our gui folder and other modules.
    
    params = [
        main_script,
        '--name=%s' % app_name,
        '--windowed', # No console
        '--onefile', # Standalone exe
        '--clean',
        '--add-data=gui:gui', # Include gui folder
        '--collect-all=customtkinter', # Ensure customtkinter is fully collected
        '--collect-all=pyzbar',
        '--collect-all=cv2',
    ]

    PyInstaller.__main__.run(params)
    print("Build complete! Check the 'dist' folder.")

if __name__ == "__main__":
    build()
