import cv2
import os
import glob
import sys

def create_qr_video(qr_folder="output_qrs", output_video="qr_transfer.mp4", fps=2):
    """
    Combine all QR code images into a single video file.
    """
    images = sorted(glob.glob(os.path.join(qr_folder, "qr_*.png")))
    if not images:
        print(f"No QR images found in {qr_folder}")
        return

    # Read the first image to get dimensions
    first_img = cv2.imread(images[0])
    height, width, layers = first_img.shape

    # Define the codec and create VideoWriter object
    # 'mp4v' is a common codec for MP4
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    print(f"Creating video: {output_video} with {len(images)} frames at {fps} FPS...")
    
    for image_path in images:
        img = cv2.imread(image_path)
        video.write(img)

    video.release()
    print("Video generation complete!")

if __name__ == "__main__":
    folder = sys.argv[1] if len(sys.argv) > 1 else "output_qrs"
    output = sys.argv[2] if len(sys.argv) > 2 else "qr_transfer.mp4"
    create_qr_video(folder, output)
