# Multiple-LSB Audio Steganography

A Python implementation of audio steganography using Multiple Least Significant Bit (LSB) technique with optional encryption.

## Features

- Hide text messages in audio files (MP3/WAV)
- Multiple LSB embedding (1-4 bits)
- Extended Vigenère cipher encryption
- Random starting position for enhanced security
- Audio quality analysis (PSNR calculation)
- GUI and command-line interfaces

## Requirements

**System Dependencies:**
- FFmpeg (required for audio processing)

**Python Dependencies:**
```bash
pip install pydub pygame tkinter
```

## Usage

### Command Line Interface
```bash
python src/main.py
```

### GUI Interface
```bash
python src/gui.py
```

## How to Use

1. **Embed Message**: Hide text in an audio file
   - Select cover audio (MP3 format recommended)
   - Enter secret message and stego key
   - Choose LSB level (1-4)
   - Optional: Enable encryption and random starting point

2. **Extract Message**: Retrieve hidden text
   - Use the same parameters as embedding
   - Provide the steganography audio file


## Project Structure

```
src/
├── main.py          # Command-line interface
├── gui.py           # Graphical user interface
├── processing.py    # Core steganography functions
└── formula.py       # Encryption and utility 

test/                # Test files and examples
assets/              # Sample audio files
```

## Authors

This project is developed for **IF4022 Cryptography** course at **Institut Teknologi Bandung (ITB)**.

**Team Members:**
- Ahmad Farid Mudrika (13522008)
- Zachary Samuel Tobing (13522016)