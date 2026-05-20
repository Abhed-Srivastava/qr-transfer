import customtkinter as ctk
from gui.dashboard import Dashboard
from gui.scanner_ui import ScannerUI
from gui.recovery_ui import RecoveryUI
import config

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QR File Transfer System Pro")
        self.geometry("1100x700")
        
        ctk.set_appearance_mode(config.THEME)
        ctk.set_default_color_theme(config.COLOR_THEME)

        # Tab View
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(expand=True, fill="both", padx=20, pady=20)
        
        self.tab_dashboard = self.tab_view.add("Dashboard")
        self.tab_scanner = self.tab_view.add("Live Scanner")
        self.tab_recovery = self.tab_view.add("Recovery")
        
        # Initialize Tab Contents
        self.dashboard = Dashboard(self.tab_dashboard)
        self.dashboard.pack(expand=True, fill="both")
        
        self.scanner_ui = ScannerUI(self.tab_scanner)
        self.scanner_ui.pack(expand=True, fill="both")
        
        self.recovery_ui = RecoveryUI(self.tab_recovery, scanner_ui=self.scanner_ui)
        self.recovery_ui.pack(expand=True, fill="both")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
