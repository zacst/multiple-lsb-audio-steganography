import formula as f
import processing as proc

def main():
    print("=== Multiple-LSB Audio Steganography ===")
    print("1. Embed message")
    print("2. Extract message")
    print("3. Check audio capacity")
    print("4. Test encryption/decryption")
    
    choice = input("\nPilih operasi (1-4): ")
    
    if choice == "1":
        # Embed message
        cover_path = input("Path audio cover (MP3): ")
        secret_message = input("Pesan secret: ")
        stego_key = input("Stego key: ")
        n_lsb = int(input("n-LSB (1-4): "))
        use_encryption = input("Gunakan enkripsi? (y/n): ").lower() == 'y'
        use_random = input("Gunakan random start? (y/n): ").lower() == 'y'
        output_path = input("Output path (default: output_stego.wav): ") or "output_stego.wav"
        
        result = proc.embed_message(
            cover_audio_path=cover_path,
            secret_message=secret_message,
            stego_key=stego_key,
            n_lsb=n_lsb,
            use_encryption=use_encryption,
            use_random_start=use_random,
            output_path=output_path
        )
        
        if result['success']:
            print(f"\n✓ Berhasil embed pesan!")
            print(f"Output: {result['output_path']}")
            print(f"PSNR: {result['psnr']:.2f} dB")
            print(f"Starting position: {result['starting_position']}")
        else:
            print(f"\n✗ Gagal: {result['error']}")
    
    elif choice == "2":
        # Extract message
        print("\n=== Ekstrak Pesan ===")
        print("Masukkan parameter yang SAMA dengan saat embedding:")
        
        stego_path = input("Path audio steganografi: ")
        stego_key = input("Stego key: ")
        n_lsb = int(input("n-LSB (1-4): "))
        use_encryption = input("Apakah pesan dienkripsi saat embed? (y/n): ").lower() == 'y'
        use_random = input("Apakah menggunakan random start saat embed? (y/n): ").lower() == 'y'
        
        result = proc.extract_message(
            stego_audio_path=stego_path,
            stego_key=stego_key,
            n_lsb=n_lsb,
            use_encryption=use_encryption,
            use_random_start=use_random
        )
        
        if result['success']:
            print(f"\n✓ Berhasil ekstrak pesan!")
            print(f"Pesan: {result['message']}")
            print(f"Panjang: {result['message_length']} karakter")
            print(f"Starting position yang digunakan: {result['starting_position']}")
        else:
            print(f"\n✗ Gagal: {result['error']}")
    
    elif choice == "3":
        # Check capacity
        audio_path = input("Path audio: ")
        n_lsb = int(input("n-LSB (1-4): "))
        
        result = proc.get_capacity(audio_path, n_lsb)
        
        if result['success']:
            print(f"\n✓ Kapasitas audio:")
            print(f"Maksimum karakter: {result['capacity_chars']}")
            print(f"Maksimum bytes: {result['capacity_bytes']}")
            print(f"Durasi audio: {result['audio_info']['duration']:.2f} detik")
        else:
            print(f"\n✗ Gagal: {result['error']}")
    
    elif choice == "4":
        # Test encryption
        plaintext = input("Plaintext: ")
        key = input("Key: ")
        
        encrypted = f.extended_vigenere_encrypt(plaintext, key)
        decrypted = f.extended_vigenere_decrypt(encrypted, key)
        
        print(f"\nPlaintext: {plaintext}")
        print(f"Encrypted: {encrypted}")
        print(f"Decrypted: {decrypted}")
        print(f"Match: {plaintext == decrypted}")

if __name__ == "__main__":
    main()