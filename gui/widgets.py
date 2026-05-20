import customtkinter as ctk

class ProgressPanel(ctk.CTkFrame):
    def __init__(self, master, title, **kwargs):
        super().__init__(master, **kwargs)
        
        self.label = ctk.CTkLabel(self, text=title, font=("Helvetica", 16, "bold"))
        self.label.pack(pady=5)
        
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(fill="x", padx=20, pady=10)
        self.progress_bar.set(0)
        
        self.status_label = ctk.CTkLabel(self, text="Status: Idle")
        self.status_label.pack(pady=5)

    def update_progress(self, current, total, status_text=None):
        if total > 0:
            val = current / total
        else:
            val = 0
        self.progress_bar.set(val)
        
        if status_text:
            self.status_label.configure(text=status_text)
        else:
            self.status_label.configure(text=f"Progress: {current}/{total} ({val:.1%})")

class StatsLabel(ctk.CTkFrame):
    def __init__(self, master, label_text, value_text="0", **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        
        self.label = ctk.CTkLabel(self, text=label_text, font=("Helvetica", 12))
        self.label.pack(side="left", padx=5)
        
        self.value = ctk.CTkLabel(self, text=value_text, font=("Helvetica", 12, "bold"))
        self.value.pack(side="left", padx=5)

    def set_value(self, val):
        self.value.configure(text=str(val))
