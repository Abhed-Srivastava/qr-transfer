# QR File Transfer System Pro

A professional-grade Python project to transfer any file offline by converting them into a sequence of QR codes, videos, or live streams.

## New Features

- **Modern GUI**: Built with `CustomTkinter` for a sleek, professional look with integrated progress bars.
- **Smart Session Management**: Every encoding session is saved in a unique timestamped folder to prevent overwriting.
- **Output Mode Selection**: Choose between QR image folders, MP4 videos, or both.
- **QR-to-Video**: Convert your QR sequence into an MP4 video for high-speed transmission.
- **Multi-Mode Scanning**: Scan from image folders, MP4 videos, or live webcam feeds.
- **Robust Recovery**: Identify exact missing chunks and recover them without restarting the transfer.
- **Advanced Metadata**: Every QR includes unique session IDs, chunk hashes, and global file integrity checks.
- **Reed-Solomon Support**: Integrated error correction for physical scanning reliability.
- **Compression Options**: Support for `zlib`, `gzip`, `lzma`, and `zstandard`.

## Project Structure

```text
project/
├── encoder.py         # File-to-QR logic
├── decoder.py         # QR-to-File logic
├── video_generator.py # QR-to-Video conversion
├── scan_video.py      # Video-to-File logic
├── live_scanner.py    # Webcam/Live scanning engine
├── recovery.py        # Missing chunk detection & recovery
├── checksum.py        # SHA256 & CRC32 verification
├── compression.py     # Multi-algorithm compression support
├── qr_utils.py        # Robust payload & session management
├── config.py          # Global settings & paths
├── gui/               # Modern CustomTkinter interface
│   ├── main_window.py # Main entry point
│   ├── dashboard.py   # Overview & Stats
│   ├── encoder_ui.py  # File-to-QR settings
│   ├── decoder_ui.py  # Standalone folder/video decoder
│   ├── scanner_ui.py  # Live scanning interface
│   ├── recovery_ui.py # Recovery & resume interface
│   └── widgets.py     # Reusable UI components
├── build_exe.py       # Standalone build script
└── requirements.txt   # Dependencies
```

## Installation

1. Install Python 3.9+.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: On Linux, install `libzbar0`: `sudo apt-get install libzbar0`*

## Usage

### GUI (Main Interface)
Launch the professional desktop application:
```bash
python main.py
```

### Building Standalone Executable
To create a standalone executable for Windows/Linux:
```bash
python build_exe.py
```
The result will be in the `dist/` folder.

### Packaged Executable Output
When the app is packaged as an executable, it stores generated files in a user-writable app folder:

- Windows: `C:\Users\<YourUser>\Documents\QRTransferPro\`
- Linux: `~/Documents/QRTransferPro/`

Inside that folder, the app creates:

- `qrs/` for generated QR images
- `videos/` for generated MP4 files
- `reconstructed/` for decoded files
- `temp/` for temporary working files

During source-code development, those folders stay inside the project directory unless you override `QR_TRANSFER_PRO_HOME`.

### Advanced Workflows

1. **Standalone Folder Decoding**:
   - Go to the **Folder Decoder** tab.
   - Browse for a folder containing QR PNG images.
   - Click **Start Reconstruction** to batch-restore all files found in that folder.
   - Alternatively, use **Scan from Video** to decode an MP4 file directly.

2. **High-Speed Transfer**:
   - Use the **Dashboard** to encode a file.
   - Use **Video Generator** to create `transfer.mp4`.
   - On the receiving end, use **Live Scanner** or **Video Scanner** to reconstruct.

2. **Recovery Mode**:
   - If a transfer is incomplete, go to the **Recovery** tab.
   - Click **Check Missing Chunks** to see what's missing.
   - Upload missing QR images or rescan the missing segments.

## Reliability & Integrity

- **Chunk Hashing**: Every QR chunk is verified using SHA256.
- **Full File Hashing**: The final reconstructed file is matched against the original's SHA256.
- **Session IDs**: Prevents mixing chunks from different files or transfer sessions.

## Limitations

- **Video FPS**: Higher FPS transfers are faster but require higher-quality cameras and better lighting.
- **QR Density**: Small chunk sizes (e.g., 200 bytes) are easier to scan but require more QR codes.

## Future Improvements

- [ ] Multi-QR frame mode (Grid of 4 QRs per frame).
- [ ] Adaptive FPS based on scan success rate.
- [ ] Mobile companion app for receiving.
