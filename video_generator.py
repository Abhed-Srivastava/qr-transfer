import cv2
import os
import glob
import config

class VideoGenerator:
    def __init__(self, qr_folder, output_video=None, fps=None, resolution=None):
        self.qr_folder = qr_folder
        self.output_video = output_video or os.path.join(config.VIDEOS_DIR, "transfer.mp4")
        self.fps = fps or config.DEFAULT_FPS
        self.resolution = resolution # (width, height)

    def generate(self, progress_callback=None):
        images = sorted(glob.glob(os.path.join(self.qr_folder, "qr_*.png")))
        if not images:
            return None

        # Determine resolution from first image if not provided
        first_img = cv2.imread(images[0])
        h, w, _ = first_img.shape
        res = self.resolution or (w, h)

        if not os.path.exists(os.path.dirname(self.output_video)):
            os.makedirs(os.path.dirname(self.output_video))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(self.output_video, fourcc, self.fps, res)

        for i, img_path in enumerate(images):
            img = cv2.imread(img_path)
            if self.resolution:
                img = cv2.resize(img, self.resolution)
            video.write(img)
            
            if progress_callback:
                progress_callback(i + 1, len(images))

        video.release()
        return self.output_video

if __name__ == "__main__":
    import sys
    folder = sys.argv[1] if len(sys.argv) > 1 else config.QRS_DIR
    gen = VideoGenerator(folder)
    path = gen.generate()
    print(f"Video saved to: {path}")
