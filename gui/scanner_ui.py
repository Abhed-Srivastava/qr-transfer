import customtkinter as ctk
import cv2
from PIL import Image, ImageTk
from live_scanner import LiveScanner
from decoder import FileDecoder
from gui.widgets import StatsLabel, ProgressPanel
import threading

class ScannerUI(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.decoder = FileDecoder()
        self.scanner = LiveScanner(decoder=self.decoder)
        
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        
        # --- Video Feed ---
        self.video_label = ctk.CTkLabel(self, text="Camera Feed Not Started", width=640, height=480, fg_color="black")
        self.video_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # --- Controls & Stats ---
        self.side_panel = ctk.CTkFrame(self)
        self.side_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.side_panel, text="Live Scanner", font=("Helvetica", 18, "bold")).pack(pady=10)
        
        self.start_btn = ctk.CTkButton(self.side_panel, text="Start Webcam", command=self.toggle_scanner)
        self.start_btn.pack(pady=10)
        
        self.fps_stat = StatsLabel(self.side_panel, "FPS:")
        self.fps_stat.pack(fill="x")
        
        self.scanned_stat = StatsLabel(self.side_panel, "Received:")
        self.scanned_stat.pack(fill="x")
        
        self.missing_stat = StatsLabel(self.side_panel, "Missing:")
        self.missing_stat.pack(fill="x")
        
        self.dupe_stat = StatsLabel(self.side_panel, "Duplicates:")
        self.dupe_stat.pack(fill="x")
        
        self.progress = ProgressPanel(self.side_panel, "Reconstruction")
        self.progress.pack(fill="x", pady=20)
        
        self.reassemble_btn = ctk.CTkButton(self.side_panel, text="Reassemble File", command=self.reassemble, state="disabled")
        self.reassemble_btn.pack(pady=10)

    def toggle_scanner(self):
        if self.scanner.is_running:
            self.scanner.stop()
            self.start_btn.configure(text="Start Webcam")
        else:
            self.scanner.is_running = True
            self.start_btn.configure(text="Stop Webcam")
            threading.Thread(target=self.run_scanner, daemon=True).start()

    def run_scanner(self):
        self.scanner.start(frame_callback=self.update_frame, status_callback=self.update_stats)

    def update_frame(self, frame):
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(rgb_frame)
        
        # Resize to fit label while maintaining aspect ratio
        w, h = self.video_label.winfo_width(), self.video_label.winfo_height()
        if w > 1 and h > 1:
            img.thumbnail((w, h))
        
        ctk_img = ImageTk.PhotoImage(img)
        self.video_label.configure(image=ctk_img, text="")
        self.video_label.image = ctk_img

    def update_stats(self, stats):
        self.fps_stat.set_value(f"{stats['fps']:.1f}")
        self.scanned_stat.set_value(stats['received'])
        self.dupe_stat.set_value(stats['duplicates'])
        
        missing_count = len(stats['missing']) if stats['missing'] else 0
        self.missing_stat.set_value(missing_count)
        
        if stats['total']:
            self.progress.update_progress(stats['received'], stats['total'])
            if stats['received'] == stats['total']:
                self.reassemble_btn.configure(state="normal")

    def reassemble(self):
        success, result = self.decoder.reassemble()
        if success:
            ctk.CTkMessagebox.show_info("Success", f"File reconstructed successfully!\nPath: {result}")
        else:
            ctk.CTkMessagebox.show_error("Error", f"Failed to reassemble: {result}")
