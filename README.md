# QR File Transfer System

A complete Python project to transfer any file (including large images) offline by converting them into a sequence of QR codes and reconstructing them back.

## Features

- **Encoder**: Compresses files using `zlib`, splits them into chunks, and generates a sequence of QR codes with metadata.
- **Decoder**: Reads QR codes from a folder, validates chunk integrity, and reconstructs the original file.
- **Webcam Scanner**: Live decoding of QR codes from a camera feed.
- **Animated QR**: Generate a video from the QR code sequence for easier transmission.
- **Reliability**: Uses SHA256 hashing to verify the integrity of the reconstructed file.
- **GUI & CLI**: Easy-to-use Tkinter interface and a powerful command-line interface.
- **Metadata**: Each QR includes filename, chunk index, total chunks, and the file hash.

## Installation

1. Ensure you have Python 3.7+ installed.
2. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: On Linux, you might need to install `libzbar0`: `sudo apt-get install libzbar0`*

## Usage

### GUI (Recommended)
Run the main application:
```bash
python main.py
```

### CLI
**Encoding a file:**
```bash
python main.py encode <file_path> --output output_qrs --size 500
```

**Decoding a folder of QRs:**
```bash
python main.py decode --input output_qrs --output reconstructed
```

### Webcam Scanner
To scan QR codes live from your webcam:
```bash
python webcam_decoder.py
```

### Animated QR Video
To create a video from your generated QR codes:
```bash
python video_generator.py output_qrs qr_transfer.mp4
```

## Architecture

- `utils.py`: Contains core logic for hashing, compression, and JSON payload handling.
- `encoder.py`: Handles file reading, chunking, and QR code generation.
- `decoder.py`: Handles QR code reading, sorting, and file reconstruction.
- `webcam_decoder.py`: Uses OpenCV and pyzbar for real-time camera scanning.
- `main.py`: Entry point for CLI and GUI.

## Limitations

- **Chunk Size**: Larger chunk sizes lead to denser QR codes, which are harder to scan with low-quality cameras. Default is 500 bytes.
- **Speed**: QR generation and decoding can be slow for very large files (e.g., >10MB) due to the large number of QR codes required.

## Future Improvements

- [ ] Add Reed-Solomon error correction for better physical scanning reliability.
- [ ] Implement multi-QR detection per frame.
- [ ] Add animated QR video generation for faster transfers.
- [ ] Support for resume interrupted transfers.

## Demonstration

1. Run `python main.py encode example.jpg`.
2. Check the `output_qrs` folder for the generated images.
3. Run `python main.py decode --input output_qrs`.
4. Verify the file in the `reconstructed` folder.
