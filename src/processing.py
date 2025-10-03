from pydub import AudioSegment
import random
from formula import extended_vigenere_encrypt, extended_vigenere_decrypt, convert_key_to_seed, calculate_audio_psnr

def embed_message(cover_audio_path: str, secret_message: str, stego_key: str, n_lsb: int = 1, 
                 use_encryption: bool = False, use_random_start: bool = False, 
                 output_path: str = "output_stego.wav") -> dict:
    """
    Menyembunyikan pesan secret ke dalam audio cover menggunakan metode multiple-LSB.
    
    Args:
        cover_audio_path (str): Path ke file audio cover (MP3)
        secret_message (str): Pesan yang akan disembunyikan
        stego_key (str): Kunci steganografi untuk randomisasi
        n_lsb (int): Jumlah bit LSB yang digunakan (1-4)
        use_encryption (bool): Apakah menggunakan enkripsi Extended Vigenère
        use_random_start (bool): Apakah menggunakan starting point random
        output_path (str): Path output file audio hasil steganografi
    
    Returns:
        dict: Informasi hasil proses steganografi
    """
    try:
        # 1. Load dan konversi audio cover
        audio = AudioSegment.from_mp3(cover_audio_path)
        raw_data = bytearray(audio.raw_data)
        
        # 2. Enkripsi pesan jika diperlukan
        if use_encryption:
            encrypted_message = extended_vigenere_encrypt(secret_message, stego_key)
            message_to_hide = encrypted_message
        else:
            message_to_hide = secret_message
        
        # 3. Konversi pesan ke bytes dan tambahkan delimiter
        message_bytes = message_to_hide.encode('utf-8')
        # Tambahkan delimiter untuk menandai akhir pesan
        delimiter = b'\x00\x00\x00\x00'  # 4 bytes null sebagai delimiter
        message_bytes += delimiter
        
        # 4. Hitung jumlah bit yang diperlukan
        total_bits_needed = len(message_bytes) * 8
        max_bits_available = len(raw_data) * n_lsb
        
        if total_bits_needed > max_bits_available:
            return {
                'success': False,
                'error': f'Pesan terlalu panjang! Diperlukan {total_bits_needed} bit, tersedia {max_bits_available} bit'
            }
        
        # 5. Tentukan posisi starting point
        if use_random_start:
            seed = convert_key_to_seed(stego_key)
            random.seed(seed)
            max_start = len(raw_data) - (total_bits_needed // n_lsb)
            starting_pos = random.randint(0, max_start)
        else:
            starting_pos = 0
        
        # 6. Simpan data audio asli untuk perhitungan PSNR
        original_data = raw_data.copy()
        
        # 7. Embed pesan menggunakan multiple-LSB
        bit_index = 0
        byte_index = 0
        
        for i in range(starting_pos, len(raw_data)):
            if byte_index >= len(message_bytes):
                break
                
            # Ambil byte dari pesan
            message_byte = message_bytes[byte_index]
            
            # Ambil n_lsb bits dari message_byte
            bits_to_embed = []
            for j in range(n_lsb):
                if bit_index + j < 8:
                    bit = (message_byte >> (7 - (bit_index + j))) & 1
                    bits_to_embed.append(bit)
                else:
                    break
            
            # Modifikasi LSB dari sample audio
            sample_byte = raw_data[i]
            
            # Clear n LSB bits
            mask = 0xFF << n_lsb
            sample_byte = sample_byte & mask
            
            # Set new LSB bits
            for j, bit in enumerate(bits_to_embed):
                sample_byte |= (bit << (n_lsb - 1 - j))
            
            raw_data[i] = sample_byte
            
            # Update indices
            bit_index += len(bits_to_embed)
            if bit_index >= 8:
                bit_index = 0
                byte_index += 1
        
        # 8. Buat audio segment baru dengan data yang sudah dimodifikasi
        stego_audio = AudioSegment(
            data=bytes(raw_data),
            sample_width=audio.sample_width,
            frame_rate=audio.frame_rate,
            channels=audio.channels
        )
        
        # 9. Export ke file output
        stego_audio.export(output_path, format="wav")
        
        # 10. Hitung PSNR
        psnr_value = calculate_audio_psnr(original_data, raw_data)
        
        return {
            'success': True,
            'output_path': output_path,
            'message_length': len(secret_message),
            'encrypted': use_encryption,
            'n_lsb': n_lsb,
            'starting_position': starting_pos,
            'psnr': psnr_value,
            'audio_info': {
                'channels': audio.channels,
                'sample_width': audio.sample_width,
                'frame_rate': audio.frame_rate,
                'duration': len(audio) / 1000.0  # in seconds
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def extract_message(stego_audio_path: str, stego_key: str, n_lsb: int = 1, 
                   use_encryption: bool = False, use_random_start: bool = False) -> dict:
    """
    Mengekstrak pesan secret dari audio yang mengandung steganografi.
    
    Args:
        stego_audio_path (str): Path ke file audio yang mengandung steganografi
        stego_key (str): Kunci steganografi untuk dekripsi dan randomisasi
        n_lsb (int): Jumlah bit LSB yang digunakan (1-4)
        use_encryption (bool): Apakah pesan dienkripsi dengan Extended Vigenère
        use_random_start (bool): Apakah menggunakan starting point random
    
    Returns:
        dict: Hasil ekstraksi pesan
    """
    try:
        # 1. Load audio steganografi
        audio = AudioSegment.from_file(stego_audio_path)
        raw_data = bytearray(audio.raw_data)
        
        # 2. Tentukan posisi starting point (sama seperti saat embed)
        if use_random_start:
            seed = convert_key_to_seed(stego_key)
            random.seed(seed)
            # Gunakan perhitungan yang sama seperti saat embed
            # Kita bisa menggunakan max yang besar karena akan stop saat menemukan delimiter
            max_start = len(raw_data) - 1000  # Buffer untuk delimiter
            starting_pos = random.randint(0, max_start) if max_start > 0 else 0
        else:
            starting_pos = 0
        
        # 3. Ekstrak bits dari LSB dengan algoritma yang konsisten dengan embed
        delimiter = b'\x00\x00\x00\x00'
        delimiter_bits = []
        
        # Konversi delimiter ke bits untuk deteksi akhir pesan
        for byte in delimiter:
            for i in range(8):
                delimiter_bits.append((byte >> (7 - i)) & 1)
        
        extracted_bits = []
        bit_index = 0
        byte_reconstruction = []
        current_byte_bits = []
        
        for i in range(starting_pos, len(raw_data)):
            sample_byte = raw_data[i]
            
            # Ekstrak n_lsb bits dari sample ini
            sample_bits = []
            for j in range(n_lsb):
                bit = (sample_byte >> (n_lsb - 1 - j)) & 1
                sample_bits.append(bit)
            
            # Distribusikan bits ke byte reconstruction
            for bit in sample_bits:
                current_byte_bits.append(bit)
                bit_index += 1
                
                # Jika sudah mengumpulkan 8 bits, buat byte
                if bit_index == 8:
                    # Buat byte dari 8 bits
                    byte_value = 0
                    for k, b in enumerate(current_byte_bits):
                        byte_value |= (b << (7 - k))
                    
                    byte_reconstruction.append(byte_value)
                    extracted_bits.extend(current_byte_bits)
                    
                    # Check untuk delimiter (4 bytes terakhir)
                    if len(byte_reconstruction) >= 4:
                        if byte_reconstruction[-4:] == [0, 0, 0, 0]:
                            # Hapus delimiter dari hasil
                            byte_reconstruction = byte_reconstruction[:-4]
                            extracted_bits = extracted_bits[:-32]  # 4 bytes = 32 bits
                            break
                    
                    # Reset untuk byte berikutnya
                    current_byte_bits = []
                    bit_index = 0
        
        # 4. Konversi ke bytes (gunakan hasil byte_reconstruction yang sudah dibuat)
        message_bytes = bytearray(byte_reconstruction)
        
        # 5. Konversi bytes ke string
        try:
            extracted_message = message_bytes.decode('utf-8')
        except UnicodeDecodeError:
            return {
                'success': False,
                'error': 'Gagal mendekode pesan. Pastikan parameter ekstraksi benar.'
            }
        
        # 6. Dekripsi jika diperlukan
        if use_encryption:
            try:
                final_message = extended_vigenere_decrypt(extracted_message, stego_key)
            except Exception as e:
                return {
                    'success': False,
                    'error': f'Gagal mendekripsi pesan: {str(e)}'
                }
        else:
            final_message = extracted_message
        
        return {
            'success': True,
            'message': final_message,
            'encrypted': use_encryption,
            'n_lsb': n_lsb,
            'starting_position': starting_pos,
            'message_length': len(final_message),
            'audio_info': {
                'channels': audio.channels,
                'sample_width': audio.sample_width,
                'frame_rate': audio.frame_rate,
                'duration': len(audio) / 1000.0
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def get_capacity(audio_path: str, n_lsb: int = 1) -> dict:
    """
    Menghitung kapasitas maksimum pesan yang dapat disembunyikan dalam audio.
    
    Args:
        audio_path (str): Path ke file audio
        n_lsb (int): Jumlah bit LSB yang digunakan
        
    Returns:
        dict: Informasi kapasitas audio
    """
    try:
        audio = AudioSegment.from_file(audio_path)
        raw_data_length = len(audio.raw_data)
        
        # Kapasitas dalam bit
        capacity_bits = raw_data_length * n_lsb
        
        # Kapasitas dalam bytes (dikurangi 4 bytes untuk delimiter)
        capacity_bytes = (capacity_bits // 8) - 4
        
        # Kapasitas dalam karakter (asumsi UTF-8)
        capacity_chars = capacity_bytes  # 1 byte per karakter untuk ASCII
        
        return {
            'success': True,
            'capacity_bits': capacity_bits,
            'capacity_bytes': capacity_bytes,
            'capacity_chars': capacity_chars,
            'audio_length_bytes': raw_data_length,
            'n_lsb': n_lsb,
            'audio_info': {
                'channels': audio.channels,
                'sample_width': audio.sample_width,
                'frame_rate': audio.frame_rate,
                'duration': len(audio) / 1000.0
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

# Testing functions (uncomment untuk testing)
# if __name__ == "__main__":
#     # Test embedding
#     result = embed_message(
#         cover_audio_path="../assets/sample_audio.mp3",
#         secret_message="Hello, this is a secret message!",
#         stego_key="mykey123",
#         n_lsb=2,
#         use_encryption=True,
#         use_random_start=True
#     )
#     print("Embed result:", result)
    
#     # Test extraction
#     if result['success']:
#         extract_result = extract_message(
#             stego_audio_path=result['output_path'],
#             stego_key="mykey123",
#             n_lsb=2,
#             use_encryption=True,
#             use_random_start=True
#         )
#         print("Extract result:", extract_result)