import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from live_scanner import LiveScanner
from decoder import FileDecoder
from gui.widgets import StatsLabel, ProgressPanel
import threading
import os

class ScannerUI(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.decoder = FileDecoder()
        self.scanner = LiveScanner(decoder=self.decoder)
        
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Video Feed ---
        self.video_container = ctk.CTkFrame(self, fg_color="black")
        self.video_container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.video_label = ctk.CTkLabel(self.video_container, text="Camera Feed Not Started", fg_color="black")
        self.video_label.pack(expand=True, fill="both")
        
        # --- Side Panel: Controls & Stats ---
        self.side_panel = ctk.CTkFrame(self)
        self.side_panel.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.side_panel, text="Live Webcam Scanner", font=("Helvetica", 18, "bold")).pack(pady=20)
        
        self.start_btn = ctk.CTkButton(self.side_panel, text="Start Webcam", 
                                       command=self.toggle_scanner, 
                                       height=40, font=("Helvetica", 14, "bold"))
        self.start_btn.pack(fill="x", padx=20, pady=10)
        
        # Stats Group
        self.stats_group = ctk.CTkFrame(self.side_panel, fg_color="transparent")
        self.stats_group.pack(fill="x", padx=10, pady=10)
        
        self.fps_stat = StatsLabel(self.stats_group, "Scan FPS:")
        self.fps_stat.pack(fill="x", pady=2)
        
        self.scanned_stat = StatsLabel(self.stats_group, "Chunks Received:")
        self.scanned_stat.pack(fill="x", pady=2)
        
        self.missing_stat = StatsLabel(self.stats_group, "Chunks Missing:")
        self.missing_stat.pack(fill="x", pady=2)
        
        self.dupe_stat = StatsLabel(self.stats_group, "Duplicates:")
        self.dupe_stat.pack(fill="x", pady=2)
        
        self.progress = ProgressPanel(self.side_panel, "Reconstruction Progress")
        self.progress.pack(fill="x", padx=20, pady=20)
        
        self.reassemble_btn = ctk.CTkButton(self.side_panel, text="Reassemble File", 
                                            command=self.reassemble, 
                                            state="disabled", fg_color="green",
                                            height=40, font=("Helvetica", 14, "bold"))
        self.reassemble_btn.pack(fill="x", padx=20, pady=10)
        
        self.log_box = ctk.CTkTextbox(self.side_panel, height=150, font=("Courier New", 11))
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

    def log(self, message):
        self.log_box.insert("end", f"{message}\n")
        self.log_box.see("end")

    def toggle_scanner(self):
        if self.scanner.is_running:
            self.scanner.stop()
            self.start_btn.configure(text="Start Webcam", fg_color=["#3B8ED0", "#1F6AA5"]) # Default blue
            self.video_label.configure(image="", text="Camera Feed Stopped")
            self.log("Scanner stopped.")
        else:
            self.scanner.is_running = True
            self.start_btn.configure(text="Stop Webcam", fg_color="#E74C3C") # Red
            self.log("Starting webcam...")
            threading.Thread(target=self.run_scanner, daemon=True).start()

    def run_scanner(self):
        try:
            self.scanner.start(frame_callback=self.update_frame, status_callback=self.update_stats)
        except Exception as e:
            self.after(0, lambda: self.log(f"Scanner Error: {str(e)}"))
            self.after(0, lambda: self.toggle_scanner())

    def update_frame(self, frame):
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        
        # Resize to fit container
        w = self.video_label.winfo_width()
        h = self.video_label.winfo_height()
        if w > 10 and h > 10:
            img.thumbnail((w, h))
        
        ctk_img = ImageTk.PhotoImage(img)
        self.after(0, lambda: self.video_label.configure(image=ctk_img, text=""))
        self.video_label.image = ctk_img

    def update_stats(self, stats):
        self.after(0, lambda: self.fps_stat.set_value(f"{stats['fps']:.1f}"))
        self.after(0, lambda: self.scanned_stat.set_value(stats['received']))
        self.after(0, lambda: self.dupe_stat.set_value(stats['duplicates']))
        
        missing_count = len(stats['missing']) if stats['missing'] else 0
        self.after(0, lambda: self.missing_stat.set_value(missing_count))
        
        if stats['total']:
            self.after(0, lambda: self.progress.update_progress(stats['received'], stats['total']))
            if stats['received'] == stats['total']:
                self.after(0, lambda: self.reassemble_btn.configure(state="normal"))

    def reassemble(self):
        # We need to reassemble all sessions found or the current one
        results = self.decoder.reassemble_all()
        for success, info in results:
            if success:
                messagebox.showinfo("Success", f"File '{info['filename']}' reconstructed successfully!\nPath: {info['path']}")
                self.log(f"Reassembled: {info['filename']}")
            else:
                err = info.get('error', 'Incomplete chunks')
                messagebox.showerror("Error", f"Failed to reassemble session {info.get('sid')}: {err}")
                self.log(f"Failed: {info.get('sid')} - {err}")
