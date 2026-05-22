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
        self.sessions = {} # sid -> {metadata, chunks}

    def reset(self):
        self.sessions = {}

    def process_qr_data(self, data):
        """Process raw QR string data and return (success, sid, payload)"""
        payload = qr_utils.parse_payload(data)
        if not payload:
            return False, None, None

        sid = payload['sid']
        if sid not in self.sessions:
            self.sessions[sid] = {
                'chunks': {},
                'total': payload['tot'],
                'filename': payload['name'],
                'file_ext': payload['ext'],
                'full_file_hash': payload['fhash'],
                'compression_algo': payload.get('comp', 'zlib')
            }

        session = self.sessions[sid]
        idx = payload['idx']
        
        if idx in session['chunks']:
            return True, sid, payload # Already have it, still a success

        # Verify chunk integrity
        chunk_data = qr_utils.get_chunk_bytes(payload)
        if checksum.calculate_sha256(chunk_data) != payload['chash']:
            return False, sid, payload

        session['chunks'][idx] = chunk_data
        return True, sid, payload

    def decode_folder(self, folder_path, progress_callback=None):
        """
        Batch decode all QR codes in a folder, supporting multiple sessions/files.
        Returns a list of results for each session.
        """
        # Find all png files recursively
        files = glob.glob(os.path.join(folder_path, "**", "*.png"), recursive=True)
        if not files:
            return []
            
        total_files = len(files)
        for i, f in enumerate(files):
            try:
                # Use PIL for better compatibility with different PNG formats
                img = Image.open(f)
                decoded = decode(img)
                for obj in decoded:
                    self.process_qr_data(obj.data.decode('utf-8'))
            except Exception as e:
                print(f"Error decoding {f}: {e}")
                continue
            
            if progress_callback:
                # current, total, status_text
                progress_callback(i + 1, total_files, f"Scanning {i+1}/{total_files} images...")
        
        return self.reassemble_all()

    def get_missing_chunks(self, sid):
        session = self.sessions.get(sid)
        if not session:
            return []
        missing = []
        for i in range(1, session['total'] + 1):
            if i not in session['chunks']:
                missing.append(i)
        return missing

    def reassemble_all(self):
        results = []
        for sid in self.sessions:
            results.append(self.reassemble_session(sid))
        return results

    def reassemble_session(self, sid):
        """Reassemble a specific session by its SID."""
        session = self.sessions.get(sid)
        if not session:
            return False, {"error": "Session not found"}
            
        missing = self.get_missing_chunks(sid)
        if missing:
            return False, {
                "sid": sid, 
                "filename": session['filename'], 
                "missing": missing,
                "total": session['total'],
                "received": len(session['chunks'])
            }

        # Sort and join
        sorted_indices = sorted(session['chunks'].keys())
        full_data = b"".join(session['chunks'][idx] for idx in sorted_indices)
        
        # Decompress
        try:
            decompressed_data = compression.decompress(full_data, session['compression_algo'])
            
            # Verify full hash
            if checksum.calculate_sha256(decompressed_data) != session['full_file_hash']:
                return False, {"sid": sid, "filename": session['filename'], "error": "Full file hash verification failed"}

            # Save
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            
            out_name = f"{session['filename']}{session['file_ext']}"
            out_path = os.path.join(self.output_dir, out_name)
            
            # If file exists, append sid to avoid overwrite if filenames are same
            if os.path.exists(out_path):
                out_name = f"{session['filename']}_{sid}{session['file_ext']}"
                out_path = os.path.join(self.output_dir, out_name)

            with open(out_path, 'wb') as f:
                f.write(decompressed_data)
            
            return True, {
                "sid": sid, 
                "filename": f"{session['filename']}{session['file_ext']}", 
                "path": out_path,
                "total": session['total']
            }
        except Exception as e:
            return False, {"sid": sid, "filename": session['filename'], "error": f"Decompression/Save error: {str(e)}"}

if __name__ == "__main__":
    import sys
    folder = sys.argv[1] if len(sys.argv) > 1 else config.QRS_DIR
    out = sys.argv[2] if len(sys.argv) > 2 else config.RECONSTRUCTED_DIR
    
    dec = FileDecoder(out)
    results = dec.decode_folder(folder, lambda c, t, s: print(f"\r{s}", end=""))
    print("\n\nBatch Decoding Results:")
    for success, info in results:
        if success:
            print(f"✅ {info['filename']} -> {info['path']}")
        else:
            if 'missing' in info:
                print(f"❌ {info['filename']} (SID: {info['sid']}): Missing {len(info['missing'])}/{info['total']} chunks")
            else:
                print(f"❌ {info['filename']} (SID: {info['sid']}): Error: {info['error']}")
