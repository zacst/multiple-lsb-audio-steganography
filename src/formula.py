import math

def extended_vigenere_encrypt(plaintext, key):
    """
    Mengenkripsi plaintext menggunakan Extended Vigenère Cipher.
    """
    ciphertext = ""
    key = key.encode('utf-8')  # Konversi kunci menjadi bytes
    index_key = 0
    
    for char in plaintext:
        # Mengenkripsi setiap karakter dengan nilai ASCII-nya
        # c = (P + K) mod 256
        p = ord(char)
        k = key[index_key]
        c = (p + k) % 256
        
        ciphertext += chr(c)
        
        # Pindah ke karakter kunci berikutnya, kembali ke awal jika sudah habis
        index_key = (index_key + 1) % len(key)
        
    return ciphertext

def extended_vigenere_decrypt(ciphertext, key):
    """
    Mendekripsi ciphertext menggunakan Extended Vigenère Cipher.
    """
    plaintext = ""
    key = key.encode('utf-8')  # Konversi kunci menjadi bytes
    index_key = 0
    
    for char in ciphertext:
        # Mendekripsi setiap karakter dengan nilai ASCII-nya
        # p = (C - K + 256) mod 256
        c = ord(char)
        k = key[index_key]
        p = (c - k + 256) % 256
        
        plaintext += chr(p)
        
        # Pindah ke karakter kunci berikutnya, kembali ke awal jika sudah habis
        index_key = (index_key + 1) % len(key)
        
    return plaintext

def calculate_audio_psnr(original_data: bytearray, modified_data: bytearray) -> float:
    """
    Menghitung PSNR antara audio asli dan audio yang telah dimodifikasi.
    
    Args:
        original_data (bytearray): Data audio asli
        modified_data (bytearray): Data audio yang telah dimodifikasi
        
    Returns:
        float: Nilai PSNR dalam dB
    """
    if len(original_data) != len(modified_data):
        raise ValueError("Panjang data audio harus sama")
    
    # Hitung MSE (Mean Square Error)
    mse = 0.0
    for i in range(len(original_data)):
        diff = int(original_data[i]) - int(modified_data[i])
        mse += diff * diff
    
    mse /= len(original_data)
    
    if mse == 0:
        return float('inf')  # Perfect quality
    
    # Hitung PSNR
    max_value = 255.0  # Untuk 8-bit audio samples
    psnr = 20 * math.log10(max_value / math.sqrt(mse))
    
    return psnr

def convert_key_to_seed(key: str):
    total = 0
    # Summing the ASCII number of each character
    for char in key:
        total += ord(char)
    return total