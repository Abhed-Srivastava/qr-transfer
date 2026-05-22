import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from encoder import FileEncoder
from video_generator import VideoGenerator
import config
from gui.widgets import ProgressPanel

class EncoderUI(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # --- Left Side: Encoder Settings ---
        self.enc_frame = ctk.CTkFrame(self)
        self.enc_frame.grid(row=0, column=0, padx=(20, 10), pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.enc_frame, text="File Encoder", font=("Helvetica", 20, "bold")).pack(pady=(20, 10))
        
        # File Selection
        self.file_info_frame = ctk.CTkFrame(self.enc_frame, fg_color="transparent")
        self.file_info_frame.pack(fill="x", padx=20, pady=10)
        
        self.file_path = ctk.StringVar(value="No file selected")
        self.file_label = ctk.CTkLabel(self.file_info_frame, textvariable=self.file_path, wraplength=350, font=("Helvetica", 12))
        self.file_label.pack(pady=5)
        
        ctk.CTkButton(self.file_info_frame, text="Select File", command=self.select_file, width=200).pack(pady=5)
        
        # Settings Group
        self.settings_frame = ctk.CTkFrame(self.enc_frame, fg_color="transparent")
        self.settings_frame.pack(fill="x", padx=20, pady=10)
        
        # Chunk Size
        ctk.CTkLabel(self.settings_frame, text="Chunk Size (bytes):", font=("Helvetica", 12)).pack(anchor="w", padx=10)
        self.chunk_size = ctk.StringVar(value=str(config.DEFAULT_CHUNK_SIZE))
        ctk.CTkEntry(self.settings_frame, textvariable=self.chunk_size).pack(fill="x", padx=10, pady=(0, 10))
        
        # Compression
        ctk.CTkLabel(self.settings_frame, text="Compression Algorithm:", font=("Helvetica", 12)).pack(anchor="w", padx=10)
        self.algo = ctk.StringVar(value=config.DEFAULT_COMPRESSION)
        ctk.CTkOptionMenu(self.settings_frame, values=config.COMPRESSION_ALGORITHMS, variable=self.algo).pack(fill="x", padx=10, pady=(0, 10))
        
        # Output Mode
        ctk.CTkLabel(self.settings_frame, text="Output Mode:", font=("Helvetica", 12, "bold")).pack(anchor="w", padx=10)
        self.output_mode = ctk.StringVar(value=config.MODE_IMAGE)
        modes = [config.MODE_IMAGE, config.MODE_VIDEO, config.MODE_BOTH]
        self.mode_menu = ctk.CTkOptionMenu(self.settings_frame, values=modes, variable=self.output_mode)
        self.mode_menu.pack(fill="x", padx=10, pady=(0, 10))
        
        # Video FPS
        ctk.CTkLabel(self.settings_frame, text="Video FPS (for Video mode):", font=("Helvetica", 12)).pack(anchor="w", padx=10)
        self.fps = ctk.StringVar(value=str(config.DEFAULT_FPS))
        ctk.CTkEntry(self.settings_frame, textvariable=self.fps).pack(fill="x", padx=10, pady=(0, 10))

        # --- Right Side: Actions & Progress ---
        self.action_frame = ctk.CTkFrame(self)
        self.action_frame.grid(row=0, column=1, padx=(10, 20), pady=20, sticky="nsew")
        
        ctk.CTkLabel(self.action_frame, text="Status & Progress", font=("Helvetica", 20, "bold")).pack(pady=(20, 10))

        self.start_btn = ctk.CTkButton(self.action_frame, text="Start Generation", 
                                       command=self.start_encoding_thread, 
                                       fg_color="green", height=50, font=("Helvetica", 16, "bold"))
        self.start_btn.pack(fill="x", padx=40, pady=30)
        
        self.progress = ProgressPanel(self.action_frame, "Generation Progress")
        self.progress.pack(fill="x", padx=40, pady=20)
        
        self.log_box = ctk.CTkTextbox(self.action_frame, height=200, font=("Courier New", 12))
        self.log_box.pack(fill="both", expand=True, padx=20, pady=20)

    def log(self, message):
        self.log_box.insert("end", f"[{os.path.basename(__file__)}] {message}\n")
        self.log_box.see("end")

    def select_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.file_path.set(path)
            self.log(f"Selected file: {os.path.basename(path)}")

    def start_encoding_thread(self):
        path = self.file_path.get()
        if not os.path.exists(path) or path == "No file selected":
            messagebox.showerror("Error", "Please select a valid file first.")
            return
        
        self.start_btn.configure(state="disabled")
        self.log_box.delete("1.0", "end")
        threading.Thread(target=self.run_encoding_workflow, daemon=True).start()

    def run_encoding_workflow(self):
        path = self.file_path.get()
        mode = self.output_mode.get()
        
        try:
            self.after(0, lambda: self.log("Starting encoding workflow..."))
            
            # Step 1: Encode to QR images
            enc = FileEncoder(
                path, 
                chunk_size=int(self.chunk_size.get()), 
                algorithm=self.algo.get()
            )
            
            self.after(0, lambda: self.log(f"Session ID: {enc.session_id}"))
            self.after(0, lambda: self.log(f"Target folder: {enc.output_dir}"))
            
            sid, qr_folder, files = enc.encode(progress_callback=self.update_progress)
            
            self.after(0, lambda: self.log(f"Successfully generated {len(files)} QR images."))
            
            # Step 2: Handle Video Generation if requested
            if mode in [config.MODE_VIDEO, config.MODE_BOTH]:
                self.after(0, lambda: self.log("Starting video generation..."))
                self.after(0, lambda: self.progress.update_progress(0, 100, "Initializing Video..."))
                
                video_name = f"{enc.session_folder_name}.mp4"
                video_out = os.path.join(config.VIDEOS_DIR, video_name)
                
                from video_generator import VideoGenerator
                gen = VideoGenerator(
                    qr_folder, 
                    fps=int(self.fps.get()),
                    output_video=video_out
                )
                video_path = gen.generate(progress_callback=self.update_video_progress)
                self.after(0, lambda: self.log(f"Video saved to: {video_path}"))
                
            self.after(0, lambda: self.log("Workflow complete!"))
            self.after(0, lambda: messagebox.showinfo("Success", f"Workflow Complete!\nSession ID: {sid}\nFolder: {qr_folder}"))
            
        except Exception as e:
            self.after(0, lambda e=e: self.log(f"ERROR: {str(e)}"))
            self.after(0, lambda e=e: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, lambda: self.start_btn.configure(state="normal"))

    def update_progress(self, current, total, status=None):
        self.after(0, lambda: self.progress.update_progress(current, total, status))

    def update_video_progress(self, current, total):
        status = f"Generating Video Frame {current}/{total}"
        self.after(0, lambda: self.progress.update_progress(current, total, status))
