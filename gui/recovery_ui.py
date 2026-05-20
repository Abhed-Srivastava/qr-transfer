import customtkinter as ctk
from tkinter import filedialog, messagebox
from decoder import FileDecoder
from recovery import RecoverySystem
from gui.widgets import ProgressPanel
import os

class RecoveryUI(ctk.CTkFrame):
    def __init__(self, master, scanner_ui=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Use the decoder from the scanner if available, else new one
        self.decoder = scanner_ui.decoder if scanner_ui else FileDecoder()
        self.recovery = RecoverySystem(self.decoder)
        
        ctk.CTkLabel(self, text="Recovery Panel", font=("Helvetica", 24, "bold")).pack(pady=20)
        
        self.status_box = ctk.CTkTextbox(self, width=500, height=200)
        self.status_box.pack(pady=10)
        
        self.progress = ProgressPanel(self, "Recovery Progress")
        self.progress.pack(fill="x", padx=50, pady=10)
        
        ctk.CTkButton(self, text="Check Missing Chunks", command=self.check_missing).pack(pady=10)
        
        self.upload_btn = ctk.CTkButton(self, text="Upload Missing QR Images", command=self.upload_qrs, fg_color="orange")
        self.upload_btn.pack(pady=10)
        
        ctk.CTkButton(self, text="Save Recovery Request", command=self.save_request).pack(pady=10)

    def check_missing(self):
        report = self.recovery.generate_recovery_report()
        self.status_box.delete("1.0", "end")
        self.status_box.insert("1.0", report)

    def upload_qrs(self):
        paths = filedialog.askopenfilenames(filetypes=[("PNG images", "*.png")])
        if paths:
            total = len(paths)
            count = 0
            for i, p in enumerate(paths):
                # Update progress
                self.progress.update_progress(i + 1, total, f"Processing recovery QR {i+1}/{total}")
                
                # We need to manually decode these images into the decoder
                from PIL import Image
                from pyzbar.pyzbar import decode
                try:
                    decoded = decode(Image.open(p))
                    for obj in decoded:
                        if self.decoder.process_qr_data(obj.data.decode('utf-8')):
                            count += 1
                except:
                    continue
            
            messagebox.showinfo("Recovery", f"Successfully recovered {count} chunks.")
            self.progress.update_progress(0, 100, "Recovery batch processed.")
            self.check_missing()

    def save_request(self):
        path = self.recovery.save_recovery_request()
        messagebox.showinfo("Success", f"Recovery request saved to: {path}")
