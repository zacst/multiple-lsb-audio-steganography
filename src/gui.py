import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class SteganographyApp:
    """
    A GUI application for audio steganography using the multiple-LSB method.
    """
    def __init__(self, master):
        self.master = master
        self.master.title("Multiple-LSB Audio Steganography")
        self.master.geometry("800x750")
        
        # Apply a theme for a modern look
        self.style = ttk.Style(self.master)
        self.style.theme_use('clam') # Popular themes: 'clam', 'alt', 'default', 'classic'

        # Configure styles for specific widgets
        self.style.configure('TLabel', font=('Helvetica', 11))
        self.style.configure('TButton', font=('Helvetica', 10, 'bold'))
        self.style.configure('TLabelframe.Label', font=('Helvetica', 12, 'bold'))
        self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Submit.TButton', foreground='white', background='#0078D7')

        # --- Initialize Application State Variables ---
        self._setup_variables()

        # --- Create and lay out the main UI components ---
        self._create_widgets()

    def _setup_variables(self):
        """Initializes all the Tkinter control variables."""
        self.cover_path_var = tk.StringVar(value="No file selected.")
        self.secret_file_path_var = tk.StringVar(value="No file selected.")
        self.plaintext_source_var = tk.StringVar(value='text_mode')
        self.random_start_var = tk.IntVar(value=0)  # Default to 'Sequential'
        self.encrypt_var = tk.IntVar(value=0)       # Default to 'Do Not Encrypt'
        self.lsb_var = tk.StringVar(value="1")      # Default to 1-LSB
        self.stego_key_var = tk.StringVar()

    def _create_widgets(self):
        """Creates and arranges all the widgets in the main window."""
        # Main container frame with padding
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Title ---
        title_label = ttk.Label(main_frame, text="Audio Steganography Tool", style='Header.TLabel')
        title_label.pack(pady=(0, 20))

        # --- 1. Cover Audio Selection ---
        cover_frame = ttk.LabelFrame(main_frame, text="1. Cover Audio File (*.mp3)", padding="10")
        cover_frame.pack(fill=tk.X, expand=True, pady=10)
        
        ttk.Button(cover_frame, text="Browse...", command=self._select_cover_file).grid(row=0, column=0, padx=(0, 10))
        ttk.Label(cover_frame, textvariable=self.cover_path_var, wraplength=500).grid(row=0, column=1, sticky="ew")
        cover_frame.columnconfigure(1, weight=1)

        # --- 2. Secret Message ---
        secret_frame = ttk.LabelFrame(main_frame, text="2. Secret Message", padding="10")
        secret_frame.pack(fill=tk.X, expand=True, pady=10)
        
        ttk.Radiobutton(secret_frame, text="Text Input", variable=self.plaintext_source_var, value='text_mode', command=self._update_plaintext_widgets).pack(anchor='w')
        ttk.Radiobutton(secret_frame, text="File Input", variable=self.plaintext_source_var, value='file_mode', command=self._update_plaintext_widgets).pack(anchor='w')

        # Container for the dynamic text/file widgets
        self.plaintext_container = ttk.Frame(secret_frame, padding=(20, 10))
        self.plaintext_container.pack(fill=tk.X, expand=True)
        
        # Text Input Widgets
        self.text_input_frame = ttk.Frame(self.plaintext_container)
        self.text_input = tk.Text(self.text_input_frame, height=5, width=60, font=('Courier', 10))
        self.text_input.pack(fill=tk.BOTH, expand=True)

        # File Input Widgets
        self.file_input_frame = ttk.Frame(self.plaintext_container)
        ttk.Button(self.file_input_frame, text="Select Secret File...", command=self._select_secret_file).grid(row=0, column=0, padx=(0, 10))
        ttk.Label(self.file_input_frame, textvariable=self.secret_file_path_var, wraplength=400).grid(row=0, column=1, sticky="ew")
        self.file_input_frame.columnconfigure(1, weight=1)

        # --- 3. Configuration Options ---
        options_frame = ttk.LabelFrame(main_frame, text="3. Configuration Options", padding="10")
        options_frame.pack(fill=tk.X, expand=True, pady=10)
        
        # Encryption
        ttk.Label(options_frame, text="Encryption:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        encrypt_radios = ttk.Frame(options_frame)
        ttk.Radiobutton(encrypt_radios, text="Enable", variable=self.encrypt_var, value=1).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(encrypt_radios, text="Disable", variable=self.encrypt_var, value=0).pack(side=tk.LEFT, padx=5)
        encrypt_radios.grid(row=0, column=1, sticky='w')

        # Randomization
        ttk.Label(options_frame, text="Start Point:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        random_radios = ttk.Frame(options_frame)
        ttk.Radiobutton(random_radios, text="Random", variable=self.random_start_var, value=1).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(random_radios, text="Sequential", variable=self.random_start_var, value=0).pack(side=tk.LEFT, padx=5)
        random_radios.grid(row=1, column=1, sticky='w')
        
        # LSB Choice
        ttk.Label(options_frame, text="n-LSB:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        lsb_radios = ttk.Frame(options_frame)
        for i in range(1, 5):
            ttk.Radiobutton(lsb_radios, text=f"{i}-bit", variable=self.lsb_var, value=str(i)).pack(side=tk.LEFT, padx=5)
        lsb_radios.grid(row=2, column=1, sticky='w')
        
        # --- 4. Stego Key ---
        key_frame = ttk.LabelFrame(main_frame, text="4. Stego Key", padding="10")
        key_frame.pack(fill=tk.X, expand=True, pady=10)
        
        self.key_entry = ttk.Entry(key_frame, textvariable=self.stego_key_var, width=50, font=('Helvetica', 11))
        self.key_entry.pack(fill=tk.X, expand=True)

        # --- 5. Submit Button ---
        submit_button = ttk.Button(main_frame, text="Process", command=self._submit_form, style='Submit.TButton', padding=10)
        submit_button.pack(pady=20)

        # --- Initialize dynamic widgets ---
        self._update_plaintext_widgets()

    def _select_cover_file(self):
        """Opens a file dialog to select the cover MP3 file."""
        filepath = filedialog.askopenfilename(
            title="Select Cover MP3 File",
            filetypes=(("MP3 files", "*.mp3"), ("All files", "*.*"))
        )
        if filepath:
            self.cover_path_var.set(filepath)
            print(f"Cover file selected: {filepath}")
        else:
            print("Cover file selection cancelled.")

    def _select_secret_file(self):
        """Opens a file dialog to select the secret message file."""
        filepath = filedialog.askopenfilename(
            title="Select Secret Message File",
            filetypes=(("All files", "*.*"), ("Text files", "*.txt"))
        )
        if filepath:
            self.secret_file_path_var.set(filepath)
            print(f"Secret file selected: {filepath}")
        else:
            print("Secret file selection cancelled.")

    def _update_plaintext_widgets(self):
        """Shows or hides the text/file input widgets based on the radio button selection."""
        mode = self.plaintext_source_var.get()
        
        # Hide both frames first
        self.text_input_frame.pack_forget()
        self.file_input_frame.pack_forget()
        
        if mode == 'text_mode':
            self.text_input_frame.pack(fill='x', expand=True)
        elif mode == 'file_mode':
            self.file_input_frame.pack(fill='x', expand=True)

    def _submit_form(self):
        """Gathers all user inputs and displays them."""
        # Retrieve all values from the control variables
        cover_file = self.cover_path_var.get()
        message_source_mode = self.plaintext_source_var.get()
        
        if message_source_mode == 'text_mode':
            secret_message_content = self.text_input.get("1.0", "end-1c") # Get text from Text widget
        else:
            secret_message_content = self.secret_file_path_var.get() # Get file path
        
        use_encryption = "Yes" if self.encrypt_var.get() == 1 else "No"
        use_random_start = "Yes" if self.random_start_var.get() == 1 else "No"
        lsb_bits = self.lsb_var.get()
        stego_key = self.stego_key_var.get()

        # Simple validation
        if "No file selected" in cover_file:
            messagebox.showerror("Error", "Please select a cover audio file.")
            return
        if not stego_key:
            messagebox.showerror("Error", "Stego Key cannot be empty.")
            return

        # Display summary
        summary = f"""
        --- Configuration Summary ---
        Cover File: {cover_file}
        Secret Message Mode: {message_source_mode}
        Secret Content/File: {secret_message_content[:100]}... 
        
        Use Encryption: {use_encryption}
        Random Start Point: {use_random_start}
        LSB Bits: {lsb_bits}
        Stego Key: {stego_key}
        """
        
        print(summary)
        messagebox.showinfo("Submission Summary", summary)


if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()