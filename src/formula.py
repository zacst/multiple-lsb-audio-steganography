import math

def extended_vigenere_encrypt(plaintext_bytes: bytes, key: str) -> bytes:
    key_bytes = key.encode('utf-8')
    ciphertext_bytes = bytearray()
    key_len = len(key_bytes)
    
    for i, p_byte in enumerate(plaintext_bytes):
        k_byte = key_bytes[i % key_len]
        c_byte = (p_byte + k_byte) % 256
        ciphertext_bytes.append(c_byte)
        
    return bytes(ciphertext_bytes)

def extended_vigenere_decrypt(ciphertext_bytes: bytes, key: str) -> bytes:
    key_bytes = key.encode('utf-8')
    plaintext_bytes = bytearray()
    key_len = len(key_bytes)
    
    for i, c_byte in enumerate(ciphertext_bytes):
        k_byte = key_bytes[i % key_len]
        p_byte = (c_byte - k_byte + 256) % 256
        plaintext_bytes.append(p_byte)
        
    return bytes(plaintext_bytes)

def calculate_audio_psnr(original_data: bytearray, modified_data: bytearray) -> float:
    if len(original_data) != len(modified_data):
        raise ValueError("Panjang data audio harus sama")
    mse = sum((int(orig) - int(mod))**2 for orig, mod in zip(original_data, modified_data)) / len(original_data)
    if mse == 0: return float('inf')
    max_value = 255.0
    psnr = 20 * math.log10(max_value / math.sqrt(mse))
    return psnr

def convert_key_to_seed(key: str) -> int:
    return sum(ord(char) for char in key)