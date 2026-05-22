import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from decoder import FileDecoder
from gui.widgets import ProgressPanel, StatsLabel
import config

class DecoderUI(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.decoder = FileDecoder()
        
        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        
        # --- Title ---
        ctk.CTkLabel(self, text="QR Folder Decoder", font=("Helvetica", 24, "bold")).grid(row=0, column=0, pady=(20, 10))
        ctk.CTkLabel(self, text="Reconstruct original files from a folder of QR images.", font=("Helvetica", 14)).grid(row=1, column=0, pady=(0, 20))

        # --- Folder Selection ---
        self.selection_frame = ctk.CTkFrame(self)
        self.selection_frame.grid(row=2, column=0, padx=40, pady=10, sticky="ew")
        self.selection_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self.selection_frame, text="QR Folder:").grid(row=0, column=0, padx=10, pady=20)
        self.folder_path = ctk.StringVar(value="No folder selected")
        self.folder_entry = ctk.CTkEntry(self.selection_frame, textvariable=self.folder_path, state="readonly")
        self.folder_entry.grid(row=0, column=1, padx=10, pady=20, sticky="ew")
        
        self.browse_btn = ctk.CTkButton(self.selection_frame, text="Browse Folder", command=self.browse_folder)
        self.browse_btn.grid(row=0, column=2, padx=10, pady=20)

        # --- Stats Frame ---
        self.stats_frame = ctk.CTkFrame(self)
        self.stats_frame.grid(row=3, column=0, padx=40, pady=10, sticky="ew")
        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.img_count_stat = StatsLabel(self.stats_frame, "Images Found:", "0")
        self.img_count_stat.grid(row=0, column=0, padx=10, pady=10)

        self.sessions_stat = StatsLabel(self.stats_frame, "Sessions Found:", "0")
        self.sessions_stat.grid(row=0, column=1, padx=10, pady=10)

        self.success_stat = StatsLabel(self.stats_frame, "Reconstructed:", "0")
        self.success_stat.grid(row=0, column=2, padx=10, pady=10)

        # --- Progress ---
        self.progress_frame = ctk.CTkFrame(self)
        self.progress_frame.grid(row=4, column=0, padx=40, pady=10, sticky="ew")
        
        self.scan_progress = ProgressPanel(self.progress_frame, "Scanning Images")
        self.scan_progress.pack(fill="x", padx=20, pady=10)

        # --- Action Buttons ---
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.action_frame.grid(row=5, column=0, pady=20)
        
        self.start_btn = ctk.CTkButton(self.action_frame, text="Start Reconstruction", 
                                       command=self.start_reconstruction_thread, 
                                       fg_color="green", height=40, font=("Helvetica", 14, "bold"))
        self.start_btn.pack(side="left", padx=10)
        
        self.video_scan_btn = ctk.CTkButton(self.action_frame, text="Scan from Video", 
                                            command=self.start_video_scan_thread, 
                                            height=40, font=("Helvetica", 14, "bold"))
        self.video_scan_btn.pack(side="left", padx=10)
        
        self.clear_btn = ctk.CTkButton(self.action_frame, text="Clear Logs", command=self.clear_logs, height=40)
        self.clear_btn.pack(side="left", padx=10)

        # --- Logs ---
        self.log_box = ctk.CTkTextbox(self, height=150)
        self.log_box.grid(row=6, column=0, padx=40, pady=(10, 20), sticky="nsew")
        self.grid_rowconfigure(6, weight=1)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.clear_logs()
            # Pre-count images
            import glob
            count = len(glob.glob(os.path.join(folder, "**", "*.png"), recursive=True))
            self.img_count_stat.set_value(count)
            self.log(f"Selected folder: {folder} ({count} images found)")

    def log(self, message):
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def clear_logs(self):
        self.log_box.delete("1.0", "end")
        self.scan_progress.update_progress(0, 100, "Idle")
        self.sessions_stat.set_value("0")
        self.success_stat.set_value("0")

    def start_video_scan_thread(self):
        video_file = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4 *.avi *.mkv *.mov")])
        if not video_file:
            return
            
        self.start_btn.configure(state="disabled")
        self.video_scan_btn.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.decoder.reset()
        self.clear_logs()
        
        from scan_video import VideoScanner
        scanner = VideoScanner(video_file, decoder=self.decoder)
        
        threading.Thread(target=self.run_video_scan, args=(scanner,), daemon=True).start()

    def run_video_scan(self, scanner):
        try:
            self.after(0, lambda: self.log(f"Starting video scan: {os.path.basename(scanner.video_path)}"))
            results = scanner.scan(progress_callback=self.update_progress)
            self.process_results(results)
        except Exception as e:
            self.after(0, lambda e=e: messagebox.showerror("Error", f"Video scan failed: {str(e)}"))
        finally:
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            self.after(0, lambda: self.video_scan_btn.configure(state="normal"))
            self.after(0, lambda: self.browse_btn.configure(state="normal"))

    def start_reconstruction_thread(self):
        folder = self.folder_path.get()
        if not os.path.exists(folder) or folder == "No folder selected":
            messagebox.showerror("Error", "Please select a valid QR folder.")
            return
            
        self.start_btn.configure(state="disabled")
        self.video_scan_btn.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.decoder.reset()
        
        threading.Thread(target=self.run_reconstruction, args=(folder,), daemon=True).start()

    def run_reconstruction(self, folder):
        try:
            self.after(0, lambda: self.log("Starting batch reconstruction..."))
            results = self.decoder.decode_folder(folder, progress_callback=self.update_progress)
            self.process_results(results)
        except Exception as e:
            self.after(0, lambda e=e: messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}"))
        finally:
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            self.after(0, lambda: self.video_scan_btn.configure(state="normal"))
            self.after(0, lambda: self.browse_btn.configure(state="normal"))

    def process_results(self, results):
        success_count = 0
        self.after(0, lambda: self.sessions_stat.set_value(len(results)))
        
        for success, info in results:
            if success:
                success_count += 1
                msg = f"✅ {info['filename']} reconstructed successfully!"
                self.after(0, lambda m=msg: self.log(m))
                self.after(0, lambda p=info['path']: self.log(f"   Saved to: {p}"))
            else:
                if 'missing' in info:
                    msg = f"❌ {info['filename']} (SID: {info['sid']}): Missing {len(info['missing'])}/{info['total']} chunks."
                    self.after(0, lambda m=msg: self.log(m))
                else:
                    msg = f"❌ {info['filename']} (SID: {info['sid']}): Error: {info['error']}"
                    self.after(0, lambda m=msg: self.log(m))
        
        self.after(0, lambda: self.success_stat.set_value(success_count))
        self.after(0, lambda c=success_count, r=len(results): messagebox.showinfo("Done", f"Reconstruction complete!\nSuccessfully restored {c}/{r} files."))

    def update_progress(self, current, total, status):
        self.after(0, lambda: self.scan_progress.update_progress(current, total, status))
