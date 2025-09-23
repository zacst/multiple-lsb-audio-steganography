import formula as f

# text input
plaintext = input("Plaintext: ")
key = input("Key: ")
plaintext_bytes = plaintext.encode('utf-8')
print(f.extended_vigenere_encrypt(plaintext, key))

# de