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


# PSNR
def calculate_psnr_signal(p_original: float, p_stego: float):
    """
    Menghitung PSNR berdasarkan kekuatan sinyal asli (P_original) dan
    sinyal steganografi (P_stego), sesuai dengan rumus yang diberikan.

    Args:
        p_original (float): Kekuatan sinyal asli.
        p_stego (float): Kekuatan sinyal setelah steganografi.

    Returns:
        float: Nilai PSNR dalam dB.
    """
    # Tangani kasus di mana penyebutnya nol untuk menghindari error
    denominator = p_stego**2 + p_original**2 - 2 * p_stego * p_original
    
    # Periksa jika penyebut sangat dekat dengan nol
    if abs(denominator) < 1e-9: # Menggunakan toleransi kecil untuk floating point
        return float('inf')

    # Hitung PSNR sesuai rumus
    psnr_value = 10 * math.log10((p_stego**2) / denominator)
    return psnr_value

# Key to seed
def convert_key_to_seed(key: str):
    total = 0
    # Summing the ASCII number of each character
    for char in key:
        total += ord(char)
    return total