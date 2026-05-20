import os

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QRS_DIR = os.path.join(BASE_DIR, "qrs")
VIDEOS_DIR = os.path.join(BASE_DIR, "videos")
RECONSTRUCTED_DIR = os.path.join(BASE_DIR, "reconstructed")
TEMP_DIR = os.path.join(BASE_DIR, "temp")

# Default settings
DEFAULT_CHUNK_SIZE = 500
DEFAULT_FPS = 12
DEFAULT_COMPRESSION = "zlib"
DEFAULT_RESOLUTION = (640, 640)

# Output Modes
MODE_IMAGE = "Image Folder"
MODE_VIDEO = "QR Video"
MODE_BOTH = "Both"

# Supported algorithms
COMPRESSION_ALGORITHMS = ["zlib", "gzip", "lzma", "zstd"]

# GUI Theme
THEME = "dark"
COLOR_THEME = "blue"
