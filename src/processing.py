from pydub import AudioSegment
import io

def process(cover_object, secret_bytes: bytes, starting_byte: int, encrypt: bool, lsb: int, stego_key: str):
    return byte_number

def get_raw_pcm_data_from_mp3(mp3_path):
    """
    Decodes an MP3 file and returns its raw PCM data as a bytes object.
    
    Args:
        mp3_path (str): The path to the input MP3 file.
        
    Returns:
        bytes: The raw audio data ready for LSB manipulation.
    """
    try:
        # 1. Load the MP3 file
        audio = AudioSegment.from_mp3(mp3_path)
        
        # 2. Export it to an in-memory WAV file to get the raw bytes
        #    - format='wav' gives you the container
        #    - audio.raw_data gives you the pure PCM sample data
        
        print(f"Successfully decoded '{mp3_path}'")
        print(f"Channels: {audio.channels}")
        print(f"Sample Width: {audio.sample_width} bytes") # e.g., 2 bytes for 16-bit audio
        print(f"Frame Rate: {audio.frame_rate} Hz")
        
        return audio.raw_data

    except Exception as e:
        print(f"Error processing MP3 file: {e}")
        return None
    
cover_file = get_raw_pcm_data_from_mp3("../assets/sample_audio.mp3")