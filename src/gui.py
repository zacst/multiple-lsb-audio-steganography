import tkinter as tk
from tkinter import filedialog, ttk

# Main window
root = tk.Tk()
root.title("Multiple-LSB Audio Steganography")
root.geometry("1600x900")

# Variables

# Cover Object
file_path_label = None

# Plaintext 
plaintext_source = tk.StringVar(value='text_mode')

# Randomization 
random_var = tk.IntVar()
random_var.set(0) # Default to 'Not Random'

# Encryption 
encryption_var = tk.IntVar()
encryption_var.set(0) # Default to 'Do Not Encrypt'

# LSB 
lsb_choice = tk.StringVar(value="1")  # Default to 1 LSB

# Functions

# Trigger function for mp3 cover object selection
def select_mp3_file():
    """Opens a file dialog for the user to select an MP3 file."""
    global selected_mp3_path
    
    # Use filedialog.askopenfilename() to open the file selection window
    filepath = filedialog.askopenfilename(
        title="Select an MP3 File",
        filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*"))
    )
    
    # Check if a file was actually selected (the user didn't click Cancel)
    if filepath:
        selected_mp3_path = filepath
        print(f"Cover file selected: {selected_mp3_path}")
        if file_path_label:
            file_path_label.config(text=f"Selected file: {filepath}")
    else:
        print("File selection cancelled.")
        if file_path_label:
            file_path_label.config(text="No file selected.")

# Trigger function for file-based plaintext
def select_file():
    """Opens a file dialog and updates the path variable."""
    global selected_file_path
    filepath = filedialog.askopenfilename(
        title="Select a File",
        filetypes=(("All files", "*.*"), ("Text files", "*.txt"))
    )
    if filepath:
        selected_file_path = filepath
        print(f"File selected: {selected_file_path}")

# Trigger function for 
def update_plaintext_source_option():
    mode = plaintext_source.get()
    
    # Hide all content frames first
    text_frame.pack_forget()
    file_frame.pack_forget()
    
    if mode == 'text_mode':
        text_frame.pack(fill='x', padx=10)
    elif mode == 'file_mode':
        file_frame.pack(fill='x', padx=10)

# Trigger function for randomization radio button
def get_random_choice():
    """This function retrieves the random value."""
    global is_random
    is_random = random_var.get()

# Trigger function for encryption radio button
def get_encryption_choice():
    """This function retrieves the encryption value."""
    global is_encrypted
    is_encrypted = encryption_var.get()

# Trigger function for LSB radio button
def get_lsb_choice():
    """This function retrieves the LSB value."""
    global lsb
    lsb = lsb_choice.get()

# Trigger function for stego key entry
def get_stego_key_input():
    """This function retrieves the stego key input value."""
    global stego_key
    stego_key = entry_stego_key.get()

# Singular function that combines all the trigger functions
def submit():
    """This function combines all the trigger functions."""
    get_encryption_choice()
    get_lsb_choice()
    get_stego_key_input()

# Frame

# Create a frame for the text-based input
text_frame = tk.Frame(root)
text_input = tk.Text(text_frame, height=5, width=40)
text_input.pack()

# Create a frame for the file-based input
file_frame = tk.Frame(root)
file_button = tk.Button(file_frame, text="Select File...", command=select_file)
file_button.pack()

# Widgets

# Label

# Title
label_title = tk.Label(root, text="Steganografi pada Berkas Audio dengan Metode Multiple-LSB")
label_title.pack() # Use a geometry manager to place the widget

# Cover Object
instruction_label = tk.Label(root, text="Select the MP3 file to be used as a cover.",
                             font=("Arial", 12), bg="#f0f0f0")
instruction_label.pack(pady=10)

# 4. Create the button that will trigger the file dialog
select_mp3_button = tk.Button(root, text="Browse for MP3", 
                           command=select_mp3_file,
                           font=("Arial", 10, "bold"),
                           bg="#4CAF50", fg="white",
                           activebackground="#45a049",
                           relief=tk.RAISED,
                           bd=3)
select_mp3_button.pack(pady=10)

# Radio buttons

# Plaintext
source_label = tk.Label(root, text="Plaintext Source:")
source_label.pack(pady=5)
# Radio button for text-based input
text_radio = tk.Radiobutton(root, 
                            text="Text-based input", 
                            variable=plaintext_source, 
                            value='text_mode',
                            command=update_plaintext_source_option)
text_radio.pack(anchor='w') # 'w' for west (left-aligned)

# Radio button for file-based input
file_radio = tk.Radiobutton(root, 
                            text="File-based input", 
                            variable=plaintext_source, 
                            value='file_mode',
                            command=update_plaintext_source_option)
file_radio.pack(anchor='w')

# Randomization
start_point_label = tk.Label(root, text="Starting Point:")
start_point_label.pack()
radio_random = tk.Radiobutton(root, text="Random", variable=random_var, value=1)
radio_random.pack()
radio_not_random = tk.Radiobutton(root, text="Not Random (Sequential)", variable=random_var, value=0)
radio_not_random.pack()

# Encryption
radio_encrypt = tk.Radiobutton(root, text="Encrypt", variable=encryption_var, value=1)
radio_encrypt.pack()
radio_no_encrypt = tk.Radiobutton(root, text="Do Not Encrypt", variable=encryption_var, value=0)
radio_no_encrypt.pack()

# LSB
label_lsb_title = tk.Label(root, text="n-LSB")
label_lsb_title.pack()
options = ["1", "2", "3", "4"]
for opt in options:
    tk.Radiobutton(root, text=opt, variable=lsb_choice, value=opt).pack(anchor="w")

# Entry

# Stego Key
label_stego_key_title = tk.Label(root, text="Stego Key")
label_stego_key_title.pack()
entry_stego_key = tk.Entry(root, width=30)
entry_stego_key.pack(padx=10, pady=10)

# Submit button
check_button = tk.Button(root, text="Submit", command=get_encryption_choice)
check_button.pack(pady=10)

# Pre-Event Initialization
update_plaintext_source_option()

# Event loop
root.mainloop()