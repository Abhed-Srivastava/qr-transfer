import cv2
from pyzbar.pyzbar import decode
from decoder import FileDecoder
import config
import os

class VideoScanner:
    def __init__(self, video_path, decoder=None):
        self.video_path = video_path
        self.decoder = decoder or FileDecoder()

    def scan(self, progress_callback=None):
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"Video not found: {self.video_path}")

        cap = cv2.VideoCapture(self.video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_idx += 1
            decoded_objs = decode(frame)
            for obj in decoded_objs:
                self.decoder.process_qr_data(obj.data.decode('utf-8'))
            
            if progress_callback:
                progress_callback(frame_idx, total_frames, f"Scanning frame {frame_idx}/{total_frames}")

        cap.release()
        return self.decoder.reassemble_all()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scan_video.py <video_path>")
        sys.exit(1)
    
    scanner = VideoScanner(sys.argv[1])
    success, result = scanner.scan(lambda c, t: print(f"\rScanning: {c}/{t}", end=""))
    print(f"\nResult: {result}")
