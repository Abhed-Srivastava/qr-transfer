import os
import qrcode
from PIL import Image
import qr_utils
import data_compression as compression
import checksum
import config
from datetime import datetime

class FileEncoder:
    def __init__(self, file_path, output_root=None, chunk_size=None, algorithm="zlib"):
        self.file_path = file_path
        self.output_root = output_root or config.QRS_DIR
        self.chunk_size = chunk_size or config.DEFAULT_CHUNK_SIZE
        self.algorithm = algorithm
        self.filename = os.path.basename(file_path)
        self.name, self.ext = os.path.splitext(self.filename)
        self.session_id = qr_utils.generate_session_id()
        
        # Create unique session folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_folder_name = f"{self.name}_{timestamp}_{self.session_id}"
        self.output_dir = os.path.join(self.output_root, self.session_folder_name)

    def encode(self, progress_callback=None):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"File not found: {self.file_path}")

        if progress_callback:
            progress_callback(0, 100, "Reading file...")

        with open(self.file_path, 'rb') as f:
            original_data = f.read()

        file_hash = checksum.calculate_sha256(original_data)
        
        if progress_callback:
            progress_callback(5, 100, "Compressing data...")
            
        # Compress
        compressed_data = compression.compress(original_data, self.algorithm)
        
        # Chunk
        chunks = [compressed_data[i:i+self.chunk_size] for i in range(0, len(compressed_data), self.chunk_size)]
        total_chunks = len(chunks)
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        generated_files = []
        for i, chunk in enumerate(chunks):
            chunk_index = i + 1
            payload = qr_utils.create_payload(
                self.session_id,
                chunk_index,
                total_chunks,
                self.name,
                self.ext,
                file_hash,
                chunk,
                self.algorithm
            )
            
            # Generate QR
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(payload)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            qr_filename = f"qr_{chunk_index:04d}.png"
            qr_path = os.path.join(self.output_dir, qr_filename)
            img.save(qr_path)
            generated_files.append(qr_path)
            
            if progress_callback:
                # Map chunk progress to 10-100% range
                p = 10 + int((chunk_index / total_chunks) * 90)
                progress_callback(p, 100, f"Generating QR {chunk_index}/{total_chunks}")
        
        return self.session_id, self.output_dir, generated_files

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python encoder.py <file_path>")
        sys.exit(1)
    
    enc = FileEncoder(sys.argv[1])
    sid, files = enc.encode()
    print(f"Session: {sid}, Generated {len(files)} QR codes.")
