import customtkinter as ctk
import os
import config

class Dashboard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # --- Title ---
        ctk.CTkLabel(self, text="QR File Transfer System Pro", font=("Helvetica", 28, "bold")).grid(row=0, column=0, pady=(40, 10))
        ctk.CTkLabel(self, text="Offline, secure, and reliable file transfer via QR codes.", font=("Helvetica", 16)).grid(row=1, column=0, pady=(0, 40), sticky="n")

        # --- Quick Stats / Info ---
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.grid(row=2, column=0, padx=40, pady=20, sticky="nsew")
        self.info_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.add_stat_box(self.info_frame, "Sessions", self.count_sessions(), 0)
        self.add_stat_box(self.info_frame, "Videos", self.count_videos(), 1)
        self.add_stat_box(self.info_frame, "Reconstructed", self.count_reconstructed(), 2)

        # --- Directory Shortcuts ---
        self.dir_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dir_frame.grid(row=3, column=0, pady=40)
        
        ctk.CTkButton(self.dir_frame, text="Open QR Folder", command=lambda: self.open_dir(config.QRS_DIR)).pack(side="left", padx=10)
        ctk.CTkButton(self.dir_frame, text="Open Videos Folder", command=lambda: self.open_dir(config.VIDEOS_DIR)).pack(side="left", padx=10)
        ctk.CTkButton(self.dir_frame, text="Open Reconstructed Folder", command=lambda: self.open_dir(config.RECONSTRUCTED_DIR)).pack(side="left", padx=10)

    def add_stat_box(self, master, label, value, col):
        box = ctk.CTkFrame(master, corner_radius=10)
        box.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        ctk.CTkLabel(box, text=value, font=("Helvetica", 32, "bold")).pack(pady=(10, 0))
        ctk.CTkLabel(box, text=label, font=("Helvetica", 14)).pack(pady=(0, 10))

    def count_sessions(self):
        try:
            return len([d for d in os.listdir(config.QRS_DIR) if os.path.isdir(os.path.join(config.QRS_DIR, d))])
        except:
            return 0

    def count_videos(self):
        try:
            return len([f for f in os.listdir(config.VIDEOS_DIR) if f.endswith(".mp4")])
        except:
            return 0

    def count_reconstructed(self):
        try:
            return len(os.listdir(config.RECONSTRUCTED_DIR))
        except:
            return 0

    def open_dir(self, path):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        
        if os.name == 'nt': # Windows
            os.startfile(path)
        elif os.name == 'posix': # Linux / Mac
            import subprocess
            subprocess.Popen(['xdg-open', path])
