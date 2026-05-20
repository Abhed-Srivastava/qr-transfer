import hashlib
import zlib
import base64
import json
import os

def calculate_sha256(data: bytes) -> str:
    """Calculate SHA256 hash of binary data."""
    return hashlib.sha256(data).hexdigest()

def compress_data(data: bytes) -> bytes:
    """Compress data using zlib."""
    return zlib.compress(data)

def decompress_data(data: bytes) -> bytes:
    """Decompress data using zlib."""
    return zlib.decompress(data)

def encode_chunk(filename: str, chunk_index: int, total_chunks: int, file_hash: str, chunk_data: bytes) -> str:
    """
    Create a JSON payload for a QR code chunk.
    Short keys are used to minimize QR code density.
    n: filename
    i: index
    t: total
    h: file hash
    d: data (base64)
    """
    payload = {
        "n": filename,
        "i": chunk_index,
        "t": total_chunks,
        "h": file_hash,
        "d": base64.b64encode(chunk_data).decode('utf-8')
    }
    return json.dumps(payload)

def decode_chunk(payload_str: str) -> dict:
    """Decode a JSON payload from a QR code."""
    try:
        return json.loads(payload_str)
    except json.JSONDecodeError:
        return None

def get_chunk_data(payload: dict) -> bytes:
    """Extract and decode base64 data from a payload."""
    return base64.b64decode(payload['d'])

def split_data(data: bytes, chunk_size: int):
    """Split data into chunks of specified size."""
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]

def ensure_dir(directory: str):
    """Ensure a directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)
