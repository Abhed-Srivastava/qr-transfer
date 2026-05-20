import json
import base64
import time
import uuid
import reedsolo
from checksum import calculate_sha256, calculate_crc32

# Initialize Reed-Solomon
rs = reedsolo.RSCodec(10) # 10 error correction bytes

def create_payload(session_id, chunk_index, total_chunks, filename, file_ext, file_hash, chunk_data, compression):
    """
    Creates a robust payload with unique addressing and metadata.
    """
    chunk_hash = calculate_sha256(chunk_data)
    chunk_crc = calculate_crc32(chunk_data)
    
    payload = {
        "sid": session_id,      # Session ID
        "idx": chunk_index,     # 1-based index
        "tot": total_chunks,    # Total chunks
        "name": filename,       # Original filename
        "ext": file_ext,        # Original extension
        "fhash": file_hash,     # Full file SHA256
        "chash": chunk_hash,    # Chunk SHA256
        "ccrc": chunk_crc,      # Chunk CRC32
        "ts": int(time.time()), # Timestamp
        "comp": compression,    # Compression algorithm used
        "data": base64.b64encode(chunk_data).decode('utf-8')
    }
    
    json_str = json.dumps(payload)
    
    # Optional: Apply Reed-Solomon to the json string for even more reliability
    # But for now, we'll stick to basic JSON to keep QR density manageable.
    return json_str

def parse_payload(payload_str):
    try:
        return json.loads(payload_str)
    except:
        return None

def get_chunk_bytes(payload):
    return base64.b64decode(payload['data'])

def generate_session_id():
    return str(uuid.uuid4())[:8]
