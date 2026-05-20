import cv2
import numpy as np
from pyzbar.pyzbar import decode
import threading
import time
from decoder import FileDecoder

class LiveScanner:
    def __init__(self, source=0, decoder=None):
        self.source = source
        self.decoder = decoder or FileDecoder()
        self.is_running = False
        self.cap = None
        self.frame = None
        self.fps = 0
        self.last_time = time.time()
        self.scan_count = 0
        self.duplicate_count = 0

    def start(self, frame_callback=None, status_callback=None):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise Exception(f"Could not open source: {self.source}")

        self.is_running = True
        
        while self.is_running:
            ret, self.frame = self.cap.read()
            if not ret:
                break

            # Calculate FPS
            curr_time = time.time()
            self.fps = 1.0 / (curr_time - self.last_time)
            self.last_time = curr_time

            # Scan frame
            decoded_objs = decode(self.frame)
            for obj in decoded_objs:
                data = obj.data.decode('utf-8')
                success = self.decoder.process_qr_data(data)
                
                if success:
                    self.scan_count += 1
                else:
                    self.duplicate_count += 1

                # Draw bounding box
                points = obj.polygon
                if len(points) > 4:
                    hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                    points = hull
                
                n = len(points)
                for j in range(0, n):
                    cv2.line(self.frame, tuple(points[j]), tuple(points[(j+1)%n]), (0, 255, 0), 3)

            if frame_callback:
                frame_callback(self.frame)
            
            if status_callback:
                stats = {
                    "fps": self.fps,
                    "scanned": self.scan_count,
                    "duplicates": self.duplicate_count,
                    "total": self.decoder.total_chunks,
                    "received": len(self.decoder.chunks),
                    "missing": self.decoder.get_missing_chunks()
                }
                status_callback(stats)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.stop()

    def stop(self):
        self.is_running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    scanner = LiveScanner()
    scanner.start()
