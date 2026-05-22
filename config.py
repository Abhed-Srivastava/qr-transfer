import os
import sys

APP_NAME = "QRTransferPro"
DATA_DIR_ENV_VAR = "QR_TRANSFER_PRO_HOME"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _get_documents_dir():
    home_dir = os.path.expanduser("~")
    documents_dir = os.path.join(home_dir, "Documents")
    if os.path.isdir(documents_dir):
        return documents_dir
    return home_dir


def get_runtime_root():
    override_dir = os.environ.get(DATA_DIR_ENV_VAR)
    if override_dir:
        return os.path.abspath(os.path.expanduser(override_dir))

    if getattr(sys, "frozen", False):
        return os.path.join(_get_documents_dir(), APP_NAME)

    return BASE_DIR


RUNTIME_ROOT = get_runtime_root()
QRS_DIR = os.path.join(RUNTIME_ROOT, "qrs")
VIDEOS_DIR = os.path.join(RUNTIME_ROOT, "videos")
RECONSTRUCTED_DIR = os.path.join(RUNTIME_ROOT, "reconstructed")
TEMP_DIR = os.path.join(RUNTIME_ROOT, "temp")


def ensure_runtime_dirs():
    for path in (QRS_DIR, VIDEOS_DIR, RECONSTRUCTED_DIR, TEMP_DIR):
        os.makedirs(path, exist_ok=True)


ensure_runtime_dirs()

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
