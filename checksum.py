import hashlib
import zlib

def calculate_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def calculate_crc32(data: bytes) -> str:
    return format(zlib.crc32(data) & 0xFFFFFFFF, '08x')

def verify_data(data: bytes, expected_sha256: str = None, expected_crc32: str = None) -> bool:
    if expected_sha256 and calculate_sha256(data) != expected_sha256:
        return False
    if expected_crc32 and calculate_crc32(data) != expected_crc32:
        return False
    return True
