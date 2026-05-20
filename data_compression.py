import zlib
import gzip
import lzma
try:
    import zstandard as zstd
except ImportError:
    zstd = None

def compress(data: bytes, algorithm: str = "zlib") -> bytes:
    if algorithm == "zlib":
        return zlib.compress(data)
    elif algorithm == "gzip":
        return gzip.compress(data)
    elif algorithm == "lzma":
        return lzma.compress(data)
    elif algorithm == "zstd":
        if zstd:
            return zstd.ZstdCompressor().compress(data)
        else:
            raise ImportError("zstandard library not installed")
    else:
        return data

def decompress(data: bytes, algorithm: str = "zlib") -> bytes:
    if algorithm == "zlib":
        return zlib.decompress(data)
    elif algorithm == "gzip":
        return gzip.decompress(data)
    elif algorithm == "lzma":
        return lzma.decompress(data)
    elif algorithm == "zstd":
        if zstd:
            return zstd.ZstdDecompressor().decompress(data)
        else:
            raise ImportError("zstandard library not installed")
    else:
        return data
