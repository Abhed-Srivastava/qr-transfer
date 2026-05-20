import os
import sys
import qrcode
from PIL import Image
import utils
import math

class FileEncoder:
    def __init__(self, file_path, output_dir="output_qrs", chunk_size=500):
        self.file_path = file_path
        self.output_dir = output_dir
        self.chunk_size = chunk_size
        self.filename = os.path.basename(file_path)

    def encode(self):
        if not os.path.exists(self.file_path):
            print(f"Error: File {self.file_path} not found.")
            return False

        print(f"Reading file: {self.filename}")
        with open(self.file_path, 'rb') as f:
            original_data = f.read()

        file_hash = utils.calculate_sha256(original_data)
        print(f"Original file hash: {file_hash}")

        print("Compressing data...")
        compressed_data = utils.compress_data(original_data)
        print(f"Compressed size: {len(compressed_data)} bytes (Ratio: {len(compressed_data)/len(original_data):.2%})")

        chunks = list(utils.split_data(compressed_data, self.chunk_size))
        total_chunks = len(chunks)
        print(f"Total chunks to generate: {total_chunks}")

        utils.ensure_dir(self.output_dir)

        for i, chunk in enumerate(chunks):
            payload = utils.encode_chunk(
                self.filename,
                i + 1,
                total_chunks,
                file_hash,
                chunk
            )

            # Create QR code
            qr = qrcode.QRCode(
                version=None, # Auto-detect
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(payload)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")
            
            # Save image
            qr_filename = f"qr_{i + 1:04d}.png"
            qr_path = os.path.join(self.output_dir, qr_filename)
            img.save(qr_path)

            # Progress
            progress = (i + 1) / total_chunks * 100
            print(f"\rGenerating QR codes: {progress:.1f}% ({i + 1}/{total_chunks})", end="", flush=True)

        print(f"\nEncoding complete! QR codes saved in: {self.output_dir}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python encoder.py <file_path> [chunk_size]")
        sys.exit(1)

    path = sys.argv[1]
    size = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    
    encoder = FileEncoder(path, chunk_size=size)
    encoder.encode()
