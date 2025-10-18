
import hashlib, json, os
from loguru import logger

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)

def read_json(path):
    if not os.path.exists(path):
        return None
    with open(path,'r', encoding='utf-8') as f:
        return json.load(f)

def structured_log(message, **ctx):
    logger.info(f"{message} | {ctx}")
