import os
import cv2
import glob
from PIL import Image
from pyzbar.pyzbar import decode
import qr_utils
import data_compression as compression
import checksum
import config

class FileDecoder:
    def __init__(self, output_dir=None):
        self.output_dir = output_dir or config.RECONSTRUCTED_DIR
        self.reset()

    def reset(self):
        self.chunks = {}
        self.total_chunks = None
        self.session_id = None
        self.filename = None
        self.file_ext = None
        self.full_file_hash = None
        self.compression_algo = "zlib"

    def process_qr_data(self, data):
        payload = qr_utils.parse_payload(data)
        if not payload:
            return False

        idx = payload['idx']
        if idx in self.chunks:
            return False # Already have it

        # Store metadata from the first chunk we see
        if self.total_chunks is None:
            self.total_chunks = payload['tot']
            self.session_id = payload['sid']
            self.filename = payload['name']
            self.file_ext = payload['ext']
            self.full_file_hash = payload['fhash']
            self.compression_algo = payload.get('comp', 'zlib')

        # Verify chunk integrity if possible
        chunk_data = qr_utils.get_chunk_bytes(payload)
        if checksum.calculate_sha256(chunk_data) != payload['chash']:
            return False

        self.chunks[idx] = chunk_data
        return True

    def decode_folder(self, folder_path, progress_callback=None):
        files = sorted(glob.glob(os.path.join(folder_path, "qr_*.png")))
        for i, f in enumerate(files):
            try:
                decoded = decode(Image.open(f))
                for obj in decoded:
                    self.process_qr_data(obj.data.decode('utf-8'))
            except:
                continue
            
            if progress_callback:
                progress_callback(i + 1, len(files))
        
        return self.reassemble()

    def get_missing_chunks(self):
        if self.total_chunks is None:
            return []
        missing = []
        for i in range(1, self.total_chunks + 1):
            if i not in self.chunks:
                missing.append(i)
        return missing

    def reassemble(self):
        missing = self.get_missing_chunks()
        if missing:
            return False, missing

        # Sort and join
        sorted_indices = sorted(self.chunks.keys())
        full_data = b"".join(self.chunks[idx] for idx in sorted_indices)
        
        # Decompress
        try:
            decompressed_data = compression.decompress(full_data, self.algorithm_from_metadata())
            
            # Verify full hash
            if checksum.calculate_sha256(decompressed_data) != self.full_file_hash:
                return False, "Hash verification failed"

            # Save
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            
            out_name = f"{self.filename}{self.file_ext}"
            out_path = os.path.join(self.output_dir, out_name)
            with open(out_path, 'wb') as f:
                f.write(decompressed_data)
            
            return True, out_path
        except Exception as e:
            return False, str(e)

    def algorithm_from_metadata(self):
        return self.compression_algo

if __name__ == "__main__":
    import sys
    folder = sys.argv[1] if len(sys.argv) > 1 else config.QRS_DIR
    out = sys.argv[2] if len(sys.argv) > 2 else config.RECONSTRUCTED_DIR
    
    dec = FileDecoder(out)
    success, result = dec.decode_folder(folder)
    if success:
        print(f"Success! File saved to: {result}")
    else:
        print(f"Failed: {result}")
