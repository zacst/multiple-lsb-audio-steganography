from pydub import AudioSegment
import random
import json
from formula import extended_vigenere_encrypt, extended_vigenere_decrypt, convert_key_to_seed, calculate_audio_psnr

POINTER_LENGTH_BYTES = 8
METADATA_HEADER_LENGTH = 4 

def _embed_bits(raw_data, bits_to_embed, start_byte_index, n_lsb):
    bit_index = 0
    total_bits = len(bits_to_embed)
    bytes_needed = (total_bits + n_lsb - 1) // n_lsb
    modified_data = raw_data[:]
    
    for i in range(bytes_needed):
        byte_index = start_byte_index + i
        if byte_index >= len(modified_data):
            break
            
        sample_byte = modified_data[byte_index]
        mask = (0xFF << n_lsb) & 0xFF
        sample_byte &= mask
        
        bits_for_this_byte = bits_to_embed[bit_index : bit_index + n_lsb]
        bit_index += n_lsb
        
        value_to_embed = 0
        for bit in bits_for_this_byte:
            value_to_embed = (value_to_embed << 1) | bit

        sample_byte |= value_to_embed
        modified_data[byte_index] = sample_byte
        
    return modified_data


def _extract_bits(raw_data, num_bits_to_extract, start_byte_index, n_lsb):
    extracted_bits = []
    bytes_to_read = (num_bits_to_extract + n_lsb - 1) // n_lsb
    
    for i in range(bytes_to_read):
        byte_index = start_byte_index + i
        if byte_index >= len(raw_data) or len(extracted_bits) >= num_bits_to_extract:
            break

        sample_byte = raw_data[byte_index]
        mask = (1 << n_lsb) - 1
        extracted_value = sample_byte & mask

        for j in range(n_lsb - 1, -1, -1):
            if len(extracted_bits) < num_bits_to_extract:
                bit = (extracted_value >> j) & 1
                extracted_bits.append(bit)
                
    return extracted_bits

def _bits_to_bytes(bits):
    b_array = bytearray()
    for i in range(0, len(bits), 8):
        byte_chunk = bits[i:i+8]
        if len(byte_chunk) < 8: continue
        byte_val = 0
        for bit in byte_chunk:
            byte_val = (byte_val << 1) | bit
        b_array.append(byte_val)
    return b_array

def _bytes_to_bits(byte_data):
    bits = []
    for byte in byte_data:
        for i in range(8):
            bits.append((byte >> (7 - i)) & 1)
    return bits

def embed_message(cover_audio_path: str, secret_data: bytes, secret_filename: str, stego_key: str, n_lsb: int, 
                  use_encryption: bool, use_random_start: bool, output_path: str) -> dict:
    try:
        audio = AudioSegment.from_file(cover_audio_path)
        original_raw_data = bytearray(audio.raw_data)
        modified_raw_data = original_raw_data[:]
        
        metadata = {
            "filename": secret_filename, 
            "filesize": len(secret_data),
            "n_lsb": n_lsb,
            "encrypted": use_encryption,
            "random_start": use_random_start
        }
        metadata_bytes = json.dumps(metadata).encode('utf-8')
        metadata_len_bytes = len(metadata_bytes).to_bytes(METADATA_HEADER_LENGTH, 'big')

        file_data_to_embed = secret_data
        if use_encryption:
            file_data_to_embed = extended_vigenere_encrypt(file_data_to_embed, stego_key)
        
        payload_bytes = metadata_len_bytes + metadata_bytes + file_data_to_embed
        payload_bits = _bytes_to_bits(payload_bytes)
        
        pointer_bits = POINTER_LENGTH_BYTES * 8
        pointer_audio_bytes_needed = (pointer_bits + n_lsb - 1) // n_lsb
        payload_audio_bytes_needed = (len(payload_bits) + n_lsb - 1) // n_lsb

        if pointer_audio_bytes_needed + payload_audio_bytes_needed > len(modified_raw_data):
            return {'success': False, 'error': 'Data rahasia terlalu besar untuk kapasitas audio.'}

        if use_random_start:
            random.seed(convert_key_to_seed(stego_key))
            min_start = pointer_audio_bytes_needed
            max_start = len(modified_raw_data) - payload_audio_bytes_needed
            starting_pos = random.randint(min_start, max_start) if min_start < max_start else min_start
        else:
            starting_pos = pointer_audio_bytes_needed

        pointer_bytes = starting_pos.to_bytes(POINTER_LENGTH_BYTES, 'big')
        pointer_bits_to_embed = _bytes_to_bits(pointer_bytes)
        
        modified_raw_data = _embed_bits(modified_raw_data, pointer_bits_to_embed, 0, n_lsb)
        modified_raw_data = _embed_bits(modified_raw_data, payload_bits, starting_pos, n_lsb)
        
        stego_audio = AudioSegment(data=bytes(modified_raw_data), sample_width=audio.sample_width, frame_rate=audio.frame_rate, channels=audio.channels)
        stego_audio.export(output_path, format="wav")
        
        psnr_value = calculate_audio_psnr(original_raw_data, modified_raw_data)
        
        return {'success': True, 'output_path': output_path, 'data_length_bytes': len(secret_data), 'starting_position': starting_pos, 'psnr': psnr_value}
        
    except Exception as e:
        return {'success': False, 'error': str(e)}

def extract_message(stego_audio_path: str, stego_key: str) -> dict:
    try:
        audio = AudioSegment.from_file(stego_audio_path)
        raw_data = bytearray(audio.raw_data)

        extracted_info = None
        for n_lsb_trial in range(1, 5):
            try:
                pointer_bits = _extract_bits(raw_data, POINTER_LENGTH_BYTES * 8, 0, n_lsb_trial)
                pointer_bytes = _bits_to_bytes(pointer_bits)
                starting_pos = int.from_bytes(pointer_bytes, 'big')

                metadata_header_bits = _extract_bits(raw_data, METADATA_HEADER_LENGTH * 8, starting_pos, n_lsb_trial)
                metadata_header_bytes = _bits_to_bytes(metadata_header_bits)
                metadata_len = int.from_bytes(metadata_header_bytes, 'big')
                
                if metadata_len > 1024:
                    continue

                current_audio_pos = starting_pos + ((METADATA_HEADER_LENGTH * 8 + n_lsb_trial - 1) // n_lsb_trial)

                metadata_bits = _extract_bits(raw_data, metadata_len * 8, current_audio_pos, n_lsb_trial)
                metadata_bytes = _bits_to_bytes(metadata_bits)
                metadata = json.loads(metadata_bytes.decode('utf-8'))

                if metadata.get('random_start', False):
                    random.seed(convert_key_to_seed(stego_key))
                    
                    payload_len = METADATA_HEADER_LENGTH + metadata_len + metadata['filesize']
                    payload_bits_len = payload_len * 8
                    payload_audio_bytes_needed = (payload_bits_len + n_lsb_trial - 1) // n_lsb_trial
                    pointer_audio_bytes_needed = (POINTER_LENGTH_BYTES * 8 + n_lsb_trial - 1) // n_lsb_trial

                    min_start = pointer_audio_bytes_needed
                    max_start = len(raw_data) - payload_audio_bytes_needed
                    
                    is_key_match = False
                    for _ in range(10):
                        rand_pos = random.randint(min_start, max_start) if min_start < max_start else min_start
                        if rand_pos == starting_pos:
                            is_key_match = True
                            break
                    
                    if not is_key_match:
                        continue

                extracted_info = {'metadata': metadata, 'starting_pos': starting_pos, 'n_lsb': n_lsb_trial}
                break

            except (json.JSONDecodeError, UnicodeDecodeError, IndexError, ValueError):
                continue

        if not extracted_info:
            return {'success': False, 'error': 'Gagal mengekstrak metadata. File mungkin rusak, kunci salah, atau bukan file stego.'}

        metadata = extracted_info['metadata']
        starting_pos = extracted_info['starting_pos']
        n_lsb = extracted_info['n_lsb']
        use_encryption = metadata.get('encrypted', False)
        
        metadata_len = len(json.dumps(metadata).encode('utf-8'))
        
        current_audio_pos = starting_pos
        current_audio_pos += ((METADATA_HEADER_LENGTH * 8 + n_lsb - 1) // n_lsb)
        current_audio_pos += ((metadata_len * 8 + n_lsb - 1) // n_lsb)
        
        file_size = metadata['filesize']
        file_data_bits = _extract_bits(raw_data, file_size * 8, current_audio_pos, n_lsb)
        extracted_data = _bits_to_bytes(file_data_bits)
        
        final_data = extracted_data
        if use_encryption:
            final_data = extended_vigenere_decrypt(extracted_data, stego_key)

        return {'success': True, 'data': final_data, 'metadata': metadata, 'starting_position': starting_pos}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': f'Terjadi kesalahan saat ekstraksi: {e}'}