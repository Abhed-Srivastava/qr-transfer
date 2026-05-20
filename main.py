import os
import sys
import argparse
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from encoder import FileEncoder
from decoder import FileDecoder

def run_cli():
    parser = argparse.ArgumentParser(description="QR File Transfer System")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Encoder command
    enc_parser = subparsers.add_parser("encode", help="Encode a file to QR codes")
    enc_parser.add_argument("file", help="Path to the file to encode")
    enc_parser.add_argument("-o", "--output", default="output_qrs", help="Output directory for QR codes")
    enc_parser.add_argument("-s", "--size", type=int, default=500, help="Chunk size in bytes (default: 500)")

    # Decoder command
    dec_parser = subparsers.add_parser("decode", help="Decode QR codes back to original file")
    dec_parser.add_argument("-i", "--input", default="output_qrs", help="Input directory containing QR codes")
    dec_parser.add_argument("-o", "--output", default="reconstructed", help="Output directory for reconstructed file")

    args = parser.parse_args()

    if args.command == "encode":
        encoder = FileEncoder(args.file, args.output, args.size)
        encoder.encode()
    elif args.command == "decode":
        decoder = FileDecoder(args.input, args.output)
        decoder.decode_folder()
    else:
        parser.print_help()
        print("\nStarting GUI instead...")
        run_gui()

class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("QR File Transfer System")
        self.root.geometry("500x400")
        
        # Style
        style = ttk.Style()
        style.configure("TButton", padding=6)
        style.configure("TFrame", padding=10)

        self.tab_control = ttk.Notebook(root)
        
        self.encode_tab = ttk.Frame(self.tab_control)
        self.decode_tab = ttk.Frame(self.tab_control)
        
        self.tab_control.add(self.encode_tab, text="Encoder")
        self.tab_control.add(self.decode_tab, text="Decoder")
        self.tab_control.pack(expand=1, fill="both")

        self.setup_encode_tab()
        self.setup_decode_tab()

    def setup_encode_tab(self):
        ttk.Label(self.encode_tab, text="Select File to Encode:").pack(pady=5)
        self.file_path_var = tk.StringVar()
        ttk.Entry(self.encode_tab, textvariable=self.file_path_var, width=50).pack(pady=5)
        ttk.Button(self.encode_tab, text="Browse", command=self.browse_file).pack(pady=5)

        ttk.Label(self.encode_tab, text="Chunk Size (bytes):").pack(pady=5)
        self.chunk_size_var = tk.StringVar(value="500")
        ttk.Entry(self.encode_tab, textvariable=self.chunk_size_var).pack(pady=5)

        ttk.Button(self.encode_tab, text="Start Encoding", command=self.start_encoding).pack(pady=20)

    def setup_decode_tab(self):
        ttk.Label(self.decode_tab, text="Select QR Folder:").pack(pady=5)
        self.qr_dir_var = tk.StringVar(value="output_qrs")
        ttk.Entry(self.decode_tab, textvariable=self.qr_dir_var, width=50).pack(pady=5)
        ttk.Button(self.decode_tab, text="Browse", command=self.browse_dir).pack(pady=5)

        ttk.Button(self.decode_tab, text="Start Decoding", command=self.start_decoding).pack(pady=20)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.file_path_var.set(filename)

    def browse_dir(self):
        directory = filedialog.askdirectory()
        if directory:
            self.qr_dir_var.set(directory)

    def start_encoding(self):
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file.")
            return
        
        try:
            size = int(self.chunk_size_var.get())
            encoder = FileEncoder(file_path, chunk_size=size)
            if encoder.encode():
                messagebox.showinfo("Success", f"QR codes generated in {encoder.output_dir}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def start_decoding(self):
        qr_dir = self.qr_dir_var.get()
        if not os.path.exists(qr_dir):
            messagebox.showerror("Error", "QR folder not found.")
            return
        
        try:
            decoder = FileDecoder(qr_dir)
            if decoder.decode_folder():
                messagebox.showinfo("Success", f"File reconstructed in {decoder.output_dir}")
            else:
                messagebox.showerror("Error", "Decoding failed. Check console for details.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

def run_gui():
    root = tk.Tk()
    app = AppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_cli()
    else:
        run_gui()
