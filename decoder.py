import os
import sys
import glob
from PIL import Image
from pyzbar.pyzbar import decode
import utils

class FileDecoder:
    def __init__(self, input_dir="output_qrs", output_dir="reconstructed"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.chunks = {}
        self.total_chunks = None
        self.original_filename = None
        self.original_hash = None

    def decode_folder(self):
        if not os.path.exists(self.input_dir):
            print(f"Error: Directory {self.input_dir} not found.")
            return False

        qr_files = glob.glob(os.path.join(self.input_dir, "*.png"))
        if not qr_files:
            print("No QR code images found in the directory.")
            return False

        print(f"Found {len(qr_files)} QR code images. Decoding...")

        for i, file_path in enumerate(qr_files):
            try:
                decoded_objects = decode(Image.open(file_path))
                if not decoded_objects:
                    print(f"Warning: Could not decode {file_path}")
                    continue

                payload_str = decoded_objects[0].data.decode('utf-8')
                payload = utils.decode_chunk(payload_str)

                if payload:
                    idx = payload['i']
                    self.chunks[idx] = utils.get_chunk_data(payload)
                    
                    # Store metadata from the first successful chunk
                    if self.total_chunks is None:
                        self.total_chunks = payload['t']
                        self.original_filename = payload['n']
                        self.original_hash = payload['h']

                progress = (i + 1) / len(qr_files) * 100
                print(f"\rDecoding progress: {progress:.1f}% ({i + 1}/{len(qr_files)})", end="", flush=True)

            except Exception as e:
                print(f"\nError processing {file_path}: {e}")

        print("\nDecoding complete. Reassembling...")
        return self.reassemble()

    def reassemble(self):
        if not self.chunks:
            print("No chunks were decoded.")
            return False

        # Check for missing chunks
        missing = []
        for i in range(1, self.total_chunks + 1):
            if i not in self.chunks:
                missing.append(i)

        if missing:
            print(f"Error: Missing {len(missing)} chunks: {missing}")
            return False

        # Sort and join chunks
        print("Sorting and joining chunks...")
        sorted_indices = sorted(self.chunks.keys())
        full_compressed_data = b"".join(self.chunks[idx] for idx in sorted_indices)

        try:
            print("Decompressing data...")
            original_data = utils.decompress_data(full_compressed_data)
            
            # Verify hash
            reconstructed_hash = utils.calculate_sha256(original_data)
            if reconstructed_hash != self.original_hash:
                print("Error: SHA256 verification failed!")
                print(f"Original: {self.original_hash}")
                print(f"Got:      {reconstructed_hash}")
                return False

            print("SHA256 verification successful!")
            
            # Save file
            utils.ensure_dir(self.output_dir)
            output_path = os.path.join(self.output_dir, self.original_filename)
            
            with open(output_path, 'wb') as f:
                f.read(original_data) if hasattr(original_data, 'read') else f.write(original_data)

            print(f"File successfully reconstructed: {output_path}")
            return True

        except Exception as e:
            print(f"Error during reassembly: {e}")
            return False

if __name__ == "__main__":
    input_folder = sys.argv[1] if len(sys.argv) > 1 else "output_qrs"
    output_folder = sys.argv[2] if len(sys.argv) > 2 else "reconstructed"
    
    decoder = FileDecoder(input_folder, output_folder)
    decoder.decode_folder()
