import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os

# Import the backend processing functions from your other file
from processing import embed_message, extract_message

class SteganographyApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Multiple-LSB Audio Steganography")

        self.style = ttk.Style(self.master)
        self.style.theme_use('clam')
        self.style.configure('TLabel', font=('Helvetica', 11))
        self.style.configure('TButton', font=('Helvetica', 10, 'bold'))
        self.style.configure('TLabelframe.Label', font=('Helvetica', 12, 'bold'))
        self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Submit.TButton', foreground='white', background='#0078D7')

        self._setup_variables()
        self._create_widgets()
        self._update_ui_for_mode()

    def _setup_variables(self):
        """Initializes all Tkinter control variables."""
        self.operation_mode_var = tk.StringVar(value='embed')
        self.audio_path_var = tk.StringVar(value="No audio file selected.")
        self.secret_file_path_var = tk.StringVar(value="No file selected.")
        self.plaintext_source_var = tk.StringVar(value='text_mode')
        self.random_start_var = tk.IntVar(value=1)
        self.encrypt_var = tk.IntVar(value=1)
        self.lsb_var = tk.StringVar(value="2")
        self.stego_key_var = tk.StringVar()

    def _create_widgets(self):
        """Creates and arranges all the widgets in the main window."""
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Audio Steganography Tool", style='Header.TLabel')
        title_label.pack(pady=(0, 20))
        
        mode_frame = ttk.LabelFrame(main_frame, text="Operation Mode", padding="10")
        mode_frame.pack(fill=tk.X, expand=True, pady=5)
        ttk.Radiobutton(mode_frame, text="Embed Message", variable=self.operation_mode_var, value='embed', command=self._update_ui_for_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Extract Message", variable=self.operation_mode_var, value='extract', command=self._update_ui_for_mode).pack(side=tk.LEFT, padx=10)

        self.audio_frame = ttk.LabelFrame(main_frame, text="1. Cover Audio File (*.mp3)", padding="10")
        self.audio_frame.pack(fill=tk.X, expand=True, pady=10)
        ttk.Button(self.audio_frame, text="Browse...", command=self._select_audio_file).grid(row=0, column=0, padx=(0, 10))
        ttk.Label(self.audio_frame, textvariable=self.audio_path_var, wraplength=500).grid(row=0, column=1, sticky="ew")
        self.audio_frame.columnconfigure(1, weight=1)

        self.secret_frame = ttk.LabelFrame(main_frame, text="2. Secret Message", padding="10")
        self.secret_frame.pack(fill=tk.X, expand=True, pady=10)
        
        ttk.Radiobutton(self.secret_frame, text="Text Input", variable=self.plaintext_source_var, value='text_mode').pack(anchor='w')
        
        text_container = ttk.Frame(self.secret_frame)
        text_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))
        
        scrollbar = ttk.Scrollbar(text_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.secret_text_input = tk.Text(
            text_container, height=5, width=60, font=('Courier', 10), 
            relief=tk.SOLID, borderwidth=1, yscrollcommand=scrollbar.set
        )
        self.secret_text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.secret_text_input.yview)
        
        ttk.Radiobutton(self.secret_frame, text="File Input (any file type)", variable=self.plaintext_source_var, value='file_mode').pack(anchor='w', pady=(10, 0))
        file_input_container = ttk.Frame(self.secret_frame)
        file_input_container.pack(fill=tk.X, expand=True, padx=20)
        ttk.Button(file_input_container, text="Select Secret File...", command=self._select_secret_file).grid(row=0, column=0, padx=(0, 10))
        ttk.Label(file_input_container, textvariable=self.secret_file_path_var, wraplength=400).grid(row=0, column=1, sticky="ew")
        file_input_container.columnconfigure(1, weight=1)

        options_frame = ttk.LabelFrame(main_frame, text="3. Configuration Options", padding="10")
        options_frame.pack(fill=tk.X, expand=True, pady=10)
        
        ttk.Label(options_frame, text="Encryption:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        encrypt_radios = ttk.Frame(options_frame)
        ttk.Radiobutton(encrypt_radios, text="Enable", variable=self.encrypt_var, value=1).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(encrypt_radios, text="Disable", variable=self.encrypt_var, value=0).pack(side=tk.LEFT, padx=5)
        encrypt_radios.grid(row=0, column=1, sticky='w')

        ttk.Label(options_frame, text="Start Point:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        random_radios = ttk.Frame(options_frame)
        ttk.Radiobutton(random_radios, text="Random", variable=self.random_start_var, value=1).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(random_radios, text="Sequential", variable=self.random_start_var, value=0).pack(side=tk.LEFT, padx=5)
        random_radios.grid(row=1, column=1, sticky='w')
        
        ttk.Label(options_frame, text="n-LSB:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        lsb_radios = ttk.Frame(options_frame)
        for i in range(1, 5):
            ttk.Radiobutton(lsb_radios, text=f"{i}-bit", variable=self.lsb_var, value=str(i)).pack(side=tk.LEFT, padx=5)
        lsb_radios.grid(row=2, column=1, sticky='w')
        
        key_frame = ttk.LabelFrame(main_frame, text="4. Stego Key", padding="10")
        key_frame.pack(fill=tk.X, expand=True, pady=10)
        self.key_entry = ttk.Entry(key_frame, textvariable=self.stego_key_var, width=50, font=('Helvetica', 11), show="*")
        self.key_entry.pack(fill=tk.X, expand=True)

        self.submit_button = ttk.Button(main_frame, text="Embed Message", command=self._process_action, style='Submit.TButton', padding=10)
        self.submit_button.pack(pady=20)

    def _select_audio_file(self):
        """Opens a file dialog with validation for MP3 (embed) or WAV (extract)."""
        mode = self.operation_mode_var.get()
        if mode == 'embed':
            title = "Select Cover MP3 File"
            filetypes = (("MP3 files", "*.mp3"),)
        else:
            title = "Select Stego WAV File"
            filetypes = (("WAV files", "*.wav"),)

        filepath = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if filepath:
            self.audio_path_var.set(filepath)

    def _select_secret_file(self):
        filepath = filedialog.askopenfilename(title="Select Secret Message File", filetypes=(("All files", "*.*"),))
        if filepath:
            self.secret_file_path_var.set(filepath)

    def _update_ui_for_mode(self):
        """Shows or hides widgets based on the selected operation mode."""
        mode = self.operation_mode_var.get()
        if mode == 'embed':
            self.audio_frame.config(text="1. Cover Audio File (*.mp3)")
            self.secret_frame.pack(fill=tk.X, expand=True, pady=10)
            self.submit_button.config(text="Embed Message")
        elif mode == 'extract':
            self.audio_frame.config(text="1. Stego Audio File (*.wav)")
            self.secret_frame.pack_forget()
            self.submit_button.config(text="Extract Message")

    def _process_action(self):
        """Gathers inputs and calls the appropriate backend function."""
        audio_file = self.audio_path_var.get()
        stego_key = self.stego_key_var.get()
        
        if "No audio file" in audio_file or not os.path.exists(audio_file):
            messagebox.showerror("Error", "Please select a valid audio file.")
            return
        if not stego_key:
            messagebox.showerror("Error", "Stego Key cannot be empty.")
            return
            
        n_lsb = int(self.lsb_var.get())
        use_encryption = bool(self.encrypt_var.get())
        use_random_start = bool(self.random_start_var.get())
        
        mode = self.operation_mode_var.get()
        if mode == 'embed':
            self._execute_embed(audio_file, stego_key, n_lsb, use_encryption, use_random_start)
        elif mode == 'extract':
            self._execute_extract(audio_file, stego_key, n_lsb, use_encryption, use_random_start)

    def _execute_embed(self, audio_file, stego_key, n_lsb, use_encryption, use_random_start):
        """Menangani proses penyisipan secara lengkap."""
        secret_data = None
        if self.plaintext_source_var.get() == 'text_mode':
            secret_text = self.secret_text_input.get("1.0", "end-1c")
            if not secret_text:
                messagebox.showerror("Error", "Pesan rahasia tidak boleh kosong.")
                return
            # Untuk teks, kita tetap harus meng-encode menjadi bytes
            secret_data = secret_text.encode('utf-8')
        else: # Mode File
            secret_file = self.secret_file_path_var.get()
            if "No file selected" in secret_file or not os.path.exists(secret_file):
                messagebox.showerror("Error", "Silakan pilih file pesan rahasia yang valid.")
                return
            try:
                # Baca file dalam mode BINER ('rb') untuk menangani SEMUA jenis file
                with open(secret_file, 'rb') as f:
                    secret_data = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membaca file rahasia:\n{e}")
                return

        if not secret_data:
            messagebox.showerror("Error", "Data rahasia kosong.")
            return

        output_path = filedialog.asksaveasfilename(
            defaultextension=".wav",
            filetypes=[("WAV files", "*.wav")],
            title="Simpan Audio Stego Sebagai..."
        )
        if not output_path:
            return

        # Kirimkan `secret_data` (yang sudah pasti bytes) ke backend
        result = embed_message(
            cover_audio_path=audio_file,
            secret_data=secret_data, # Mengirim bytes secara langsung
            stego_key=stego_key, n_lsb=n_lsb,
            use_encryption=use_encryption, use_random_start=use_random_start,
            output_path=output_path
        )
        
        if result['success']:
            info = (f"Data berhasil disisipkan!\n\n"
                    f"File Output: {result['output_path']}\n"
                    f"PSNR: {result.get('psnr', 'N/A'):.2f} dB\n"
                    f"Posisi Awal: {result['starting_position']}\n"
                    f"Ukuran Data: {result.get('data_length_bytes', 'N/A')} bytes")
            messagebox.showinfo("Sukses", info)
        else:
            messagebox.showerror("Penyisipan Gagal", result['error'])

    def _execute_extract(self, audio_file, stego_key, n_lsb, use_encryption, use_random_start):
        """Menangani proses ekstraksi secara lengkap."""
        result = extract_message(
            stego_audio_path=audio_file,
            stego_key=stego_key, n_lsb=n_lsb,
            use_encryption=use_encryption, use_random_start=use_random_start
        )
        
        if result['success']:
            # Hasil ekstraksi sekarang selalu berupa bytes.
            # Tawarkan pengguna untuk menyimpannya ke file.
            extracted_data = result['message']
            
            save = messagebox.askyesno(
                "Ekstraksi Berhasil",
                f"Data berhasil diekstrak ({len(extracted_data)} bytes).\n\n"
                "Apakah Anda ingin menyimpannya ke sebuah file?"
            )
            if save:
                output_path = filedialog.asksaveasfilename(title="Simpan File Hasil Ekstraksi...")
                if output_path:
                    try:
                        with open(output_path, 'wb') as f:
                            f.write(extracted_data)
                        messagebox.showinfo("Sukses", f"File hasil ekstraksi disimpan di:\n{output_path}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Gagal menyimpan file:\n{e}")
        else:
            messagebox.showerror("Ekstraksi Gagal", result['error'])

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()