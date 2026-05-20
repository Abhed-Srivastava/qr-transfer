import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
from encoder import FileEncoder
from video_generator import VideoGenerator
import config
from gui.widgets import ProgressPanel

class Dashboard(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # --- Encoder Section ---
        self.enc_frame = ctk.CTkFrame(self)
        self.enc_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(self.enc_frame, text="File Encoder", font=("Helvetica", 18, "bold")).pack(pady=10)
        
        self.file_path = ctk.StringVar(value="No file selected")
        ctk.CTkLabel(self.enc_frame, textvariable=self.file_path, wraplength=200).pack(pady=5)
        
        ctk.CTkButton(self.enc_frame, text="Select File", command=self.select_file).pack(pady=10)
        
        # Settings
        ctk.CTkLabel(self.enc_frame, text="Chunk Size (bytes):").pack()
        self.chunk_size = ctk.StringVar(value=str(config.DEFAULT_CHUNK_SIZE))
        ctk.CTkEntry(self.enc_frame, textvariable=self.chunk_size).pack(pady=5)
        
        ctk.CTkLabel(self.enc_frame, text="Compression:").pack()
        self.algo = ctk.StringVar(value=config.DEFAULT_COMPRESSION)
        ctk.CTkOptionMenu(self.enc_frame, values=config.COMPRESSION_ALGORITHMS, variable=self.algo).pack(pady=5)
        
        # Output Mode Selection
        ctk.CTkLabel(self.enc_frame, text="Output Mode:", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
        self.output_mode = ctk.StringVar(value=config.MODE_IMAGE)
        modes = [config.MODE_IMAGE, config.MODE_VIDEO, config.MODE_BOTH]
        self.mode_menu = ctk.CTkOptionMenu(self.enc_frame, values=modes, variable=self.output_mode)
        self.mode_menu.pack(pady=5)
        
        # FPS Setting (for video mode)
        ctk.CTkLabel(self.enc_frame, text="Video FPS:").pack()
        self.fps = ctk.StringVar(value=str(config.DEFAULT_FPS))
        ctk.CTkEntry(self.enc_frame, textvariable=self.fps).pack(pady=5)

        self.start_btn = ctk.CTkButton(self.enc_frame, text="Start Generation", command=self.start_encoding_thread, fg_color="green")
        self.start_btn.pack(pady=20)
        
        self.progress = ProgressPanel(self.enc_frame, "Generation Progress")
        self.progress.pack(fill="x", padx=20, pady=10)

    def select_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.file_path.set(path)

    def start_encoding_thread(self):
        path = self.file_path.get()
        if not os.path.exists(path):
            messagebox.showerror("Error", "Please select a valid file first.")
            return
        
        self.start_btn.configure(state="disabled")
        threading.Thread(target=self.run_encoding_workflow, daemon=True).start()

    def run_encoding_workflow(self):
        path = self.file_path.get()
        mode = self.output_mode.get()
        
        try:
            # Step 1: Encode to QR images
            enc = FileEncoder(
                path, 
                chunk_size=int(self.chunk_size.get()), 
                algorithm=self.algo.get()
            )
            
            sid, qr_folder, files = enc.encode(progress_callback=self.update_progress)
            
            # Step 2: Handle Video Generation if requested
            if mode in [config.MODE_VIDEO, config.MODE_BOTH]:
                self.progress.update_progress(0, 100, "Initializing Video Generation...")
                gen = VideoGenerator(
                    qr_folder, 
                    fps=int(self.fps.get()),
                    output_video=os.path.join(config.VIDEOS_DIR, f"{enc.session_folder_name}.mp4")
                )
                video_path = gen.generate(progress_callback=self.update_video_progress)
                
                # If ONLY video was requested, we could delete the images, but user said "Do NOT remove original QR image workflow"
                # So we keep them.
                
            messagebox.showinfo("Success", f"Workflow Complete!\nSession ID: {sid}\nFolder: {qr_folder}")
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.after(0, lambda: self.start_btn.configure(state="normal"))

    def update_progress(self, current, total, status=None):
        self.after(0, lambda: self.progress.update_progress(current, total, status))

    def update_video_progress(self, current, total):
        # Video generation is the second half of the progress if "Both" is selected
        status = f"Generating Video Frame {current}/{total}"
        self.after(0, lambda: self.progress.update_progress(current, total, status))
