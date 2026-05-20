import cv2
from pyzbar.pyzbar import decode
import utils
import os
import sys

class WebcamDecoder:
    def __init__(self, output_dir="reconstructed"):
        self.output_dir = output_dir
        self.chunks = {}
        self.total_chunks = None
        self.original_filename = None
        self.original_hash = None

    def start_scanning(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Error: Could not open webcam.")
            return

        print("Webcam scanner started. Press 'q' to quit.")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Decode QR codes in the frame
            decoded_objects = decode(frame)
            
            for obj in decoded_objects:
                payload_str = obj.data.decode('utf-8')
                payload = utils.decode_chunk(payload_str)
                
                if payload:
                    idx = payload['i']
                    if idx not in self.chunks:
                        self.chunks[idx] = utils.get_chunk_data(payload)
                        
                        if self.total_chunks is None:
                            self.total_chunks = payload['t']
                            self.original_filename = payload['n']
                            self.original_hash = payload['h']
                        
                        print(f"Received chunk {idx}/{self.total_chunks}")

                # Draw a box around the QR code
                (x, y, w, h) = obj.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Chunk {payload['i'] if payload else '?'}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Display progress on screen
            if self.total_chunks:
                received = len(self.chunks)
                progress = (received / self.total_chunks) * 100
                status_text = f"Progress: {progress:.1f}% ({received}/{self.total_chunks})"
                cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
                
                if received == self.total_chunks:
                    cv2.putText(frame, "ALL CHUNKS RECEIVED! Press 'q' to reassemble.", (10, 70), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            cv2.imshow("QR Scanner", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if self.chunks and len(self.chunks) == self.total_chunks:
            return self.reassemble()
        else:
            print("Scanner closed before all chunks were received.")
            return False

    def reassemble(self):
        print("Reassembling file...")
        sorted_indices = sorted(self.chunks.keys())
        full_compressed_data = b"".join(self.chunks[idx] for idx in sorted_indices)

        try:
            original_data = utils.decompress_data(full_compressed_data)
            reconstructed_hash = utils.calculate_sha256(original_data)
            
            if reconstructed_hash == self.original_hash:
                print("SHA256 verification successful!")
                utils.ensure_dir(self.output_dir)
                output_path = os.path.join(self.output_dir, self.original_filename)
                with open(output_path, 'wb') as f:
                    f.write(original_data)
                print(f"File saved to: {output_path}")
                return True
            else:
                print("SHA256 verification failed!")
                return False
        except Exception as e:
            print(f"Error: {e}")
            return False

if __name__ == "__main__":
    scanner = WebcamDecoder()
    scanner.start_scanning()
