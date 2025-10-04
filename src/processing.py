from pydub import AudioSegment
import random
# Asumsikan fungsi lain Anda berada di file 'formula.py'
from formula import extended_vigenere_encrypt, extended_vigenere_decrypt, convert_key_to_seed, calculate_audio_psnr

# Ukuran header metadata (panjang pesan) dalam byte.
METADATA_LENGTH_BYTES = 4 

def _embed_bits(raw_data, bits_to_embed, start_byte_index, n_lsb):
    """Fungsi pembantu untuk menyisipkan bit ke dalam raw_data."""
    bit_index = 0
    total_bits = len(bits_to_embed)
    
    # Hitung berapa banyak byte audio yang dibutuhkan
    bytes_needed = (total_bits + n_lsb - 1) // n_lsb
    
    for i in range(bytes_needed):
        byte_index = start_byte_index + i
        if byte_index >= len(raw_data):
            break
            
        sample_byte = raw_data[byte_index]
        mask = (0xFF << n_lsb) & 0xFF
        sample_byte &= mask
        
        for j in range(n_lsb):
            if bit_index < total_bits:
                sample_byte |= (bits_to_embed[bit_index] << (n_lsb - 1 - j))
                bit_index += 1
        
        raw_data[byte_index] = sample_byte

def _extract_bits(raw_data, num_bits_to_extract, start_byte_index, n_lsb):
    """Fungsi pembantu untuk mengekstrak bit dari raw_data."""
    extracted_bits = []
    
    # Hitung berapa banyak byte audio yang perlu dibaca
    bytes_to_read = (num_bits_to_extract + n_lsb - 1) // n_lsb
    
    for i in range(bytes_to_read):
        byte_index = start_byte_index + i
        if byte_index >= len(raw_data):
            break

        sample_byte = raw_data[byte_index]
        for j in range(n_lsb):
            if len(extracted_bits) < num_bits_to_extract:
                bit = (sample_byte >> (n_lsb - 1 - j)) & 1
                extracted_bits.append(bit)
                
    return extracted_bits

def _bits_to_bytes(bits):
    """Mengonversi list of bits menjadi bytearray."""
    b_array = bytearray()
    for i in range(0, len(bits), 8):
        byte_chunk = bits[i:i+8]
        if len(byte_chunk) < 8: continue # Abaikan bit sisa jika tidak kelipatan 8
        byte_val = 0
        for bit in byte_chunk:
            byte_val = (byte_val << 1) | bit
        b_array.append(byte_val)
    return b_array

def _bytes_to_bits(byte_data):
    """Mengonversi bytes menjadi list of bits."""
    bits = []
    for byte in byte_data:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits

def embed_message(cover_audio_path: str, secret_data: bytes, stego_key: str, n_lsb: int = 1, 
                  use_encryption: bool = False, use_random_start: bool = False, 
                  output_path: str = "output_stego.wav") -> dict:
    """
    Menyembunyikan data rahasia (dalam format bytes):
    1. Header panjang data disisipkan di awal file (posisi tetap).
    2. Isi data disisipkan di posisi acak (jika diaktifkan).
    """
    try:
        audio = AudioSegment.from_file(cover_audio_path)
        raw_data = bytearray(audio.raw_data)
        
        # TERIMA DATA SEBAGAI BYTES, TIDAK PERLU ENCODE LAGI
        message_bytes = secret_data
        
        if use_encryption:
            # Fungsi enkripsi sekarang juga harus menerima dan mengembalikan bytes
            message_bytes = extended_vigenere_encrypt(message_bytes, stego_key)
        
        # 1. Siapkan header dan data pesan
        message_len = len(message_bytes)
        len_bytes = message_len.to_bytes(METADATA_LENGTH_BYTES, 'big')
        
        header_bits = _bytes_to_bits(len_bytes)
        message_bits = _bytes_to_bits(message_bytes)

        # 2. Hitung kebutuhan ruang dan periksa kapasitas
        header_bytes_needed = (len(header_bits) + n_lsb - 1) // n_lsb
        message_bytes_needed = (len(message_bits) + n_lsb - 1) // n_lsb
        
        if header_bytes_needed + message_bytes_needed > len(raw_data):
            return {'success': False, 'error': 'Data rahasia terlalu besar untuk kapasitas audio.'}

        original_data = raw_data.copy()

        # 3. Sisipkan header di posisi tetap (awal file)
        _embed_bits(raw_data, header_bits, 0, n_lsb)
        
        # 4. Tentukan posisi awal untuk isi pesan
        if use_random_start:
            random.seed(convert_key_to_seed(stego_key))
            max_start = len(raw_data) - message_bytes_needed
            min_start = header_bytes_needed 
            if min_start >= max_start:
                starting_pos = min_start
            else:
                starting_pos = random.randint(min_start, max_start)
        else:
            starting_pos = header_bytes_needed
            
        # 5. Sisipkan isi pesan di posisi yang telah ditentukan
        _embed_bits(raw_data, message_bits, starting_pos, n_lsb)
        
        stego_audio = AudioSegment(data=bytes(raw_data), sample_width=audio.sample_width, frame_rate=audio.frame_rate, channels=audio.channels)
        stego_audio.export(output_path, format="wav")
        
        psnr_value = calculate_audio_psnr(original_data, raw_data)
        
        # Ganti 'message_length' dengan panjang data dalam byte
        return {'success': True, 'output_path': output_path, 'data_length_bytes': len(secret_data), 'encrypted': use_encryption, 'n_lsb': n_lsb, 'starting_position': starting_pos, 'psnr': psnr_value}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def extract_message(stego_audio_path: str, stego_key: str, n_lsb: int = 1, 
                    use_encryption: bool = False, use_random_start: bool = False) -> dict:
    """
    Mengekstrak data rahasia (sebagai bytes):
    1. Membaca header dari awal file untuk mengetahui panjang data.
    2. Menghitung posisi data (acak/tetap) dan mengekstraknya.
    """
    try:
        audio = AudioSegment.from_file(stego_audio_path)
        raw_data = bytearray(audio.raw_data)
        
        # 1. Ekstrak header dari posisi tetap (awal file) untuk mendapatkan panjang pesan
        header_bits_to_extract = METADATA_LENGTH_BYTES * 8
        extracted_header_bits = _extract_bits(raw_data, header_bits_to_extract, 0, n_lsb)
        
        header_bytes = _bits_to_bytes(extracted_header_bits)
        if len(header_bytes) < METADATA_LENGTH_BYTES:
            return {'success': False, 'error': 'Gagal membaca header, file mungkin rusak atau terlalu kecil.'}
            
        message_len = int.from_bytes(header_bytes, 'big')
        
        # 2. Setelah panjang pesan diketahui, hitung posisi awal isi pesan
        header_bytes_needed = (header_bits_to_extract + n_lsb - 1) // n_lsb
        message_bits_to_extract = message_len * 8
        message_bytes_needed = (message_bits_to_extract + n_lsb - 1) // n_lsb

        if use_random_start:
            random.seed(convert_key_to_seed(stego_key))
            max_start = len(raw_data) - message_bytes_needed
            min_start = header_bytes_needed
            if min_start >= max_start:
                starting_pos = min_start
            else:
                starting_pos = random.randint(min_start, max_start)
        else:
            starting_pos = header_bytes_needed
            
        # 3. Ekstrak isi pesan dari posisi yang telah dihitung
        extracted_message_bits = _extract_bits(raw_data, message_bits_to_extract, starting_pos, n_lsb)
        message_bytes = _bits_to_bytes(extracted_message_bits)
        
        # 4. Lakukan dekripsi jika perlu (hasilnya tetap bytes)
        if use_encryption:
            final_data = extended_vigenere_decrypt(message_bytes, stego_key)
        else:
            final_data = message_bytes
        
        # HAPUS PROSES DECODING. KEMBALIKAN SEBAGAI BYTES MENTAH.
        # GUI akan menangani cara menampilkan/menyimpan data ini.
        return {'success': True, 'message': final_data, 'encrypted': use_encryption, 'n_lsb': n_lsb, 'starting_position': starting_pos, 'data_length_bytes': len(final_data)}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

# --- Contoh Penggunaan (Hapus komentar untuk mencoba) ---
if __name__ == "__main__":
    secret_text = "Ini adalah pesan rahasia baru yang seharusnya berfungsi dengan benar sekarang."
    
    # Tes menyisipkan pesan
    print("--- Proses Penyisipan ---")
    embed_result = embed_message(
        cover_audio_path="../assets/sample_audio.mp3", # Pastikan path ini benar
        secret_message=secret_text,
        stego_key="kuncisaya123",
        n_lsb=2,
        use_encryption=True,
        use_random_start=True
    )
    print("Hasil penyisipan:", embed_result)
    
    # Tes mengekstrak pesan
    if embed_result.get('success'):
        print("\n--- Proses Ekstraksi ---")
        extract_result = extract_message(
            stego_audio_path=embed_result['output_path'],
            stego_key="kuncisaya123",
            n_lsb=2,
            use_encryption=True,
            use_random_start=True
        )
        print("Hasil ekstraksi:", extract_result)
        
        # Pengecekan keberhasilan yang lebih baik
        if extract_result.get('success') and extract_result.get('message') == secret_text:
            print("\nBERHASIL: Pesan asli dan hasil ekstraksi cocok!")
        else:
            print("\nGAGAL: Pesan asli dan hasil ekstraksi TIDAK COCOK.")