import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import pygame
from processing import embed_message, extract_message

class SteganographyApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Multiple-LSB Audio Steganography")
        self.master.geometry("800x750")

        self.style = ttk.Style(self.master)
        self.style.theme_use('clam')
        self.style.configure('TLabel', font=('Helvetica', 11))
        self.style.configure('TButton', font=('Helvetica', 10, 'bold'))
        self.style.configure('TLabelframe.Label', font=('Helvetica', 12, 'bold'))
        self.style.configure('Header.TLabel', font=('Helvetica', 16, 'bold'))
        self.style.configure('Submit.TButton', foreground='white', background='#0078D7')

        pygame.init()
        pygame.mixer.init()
        self.is_playing = False
        self.stego_audio_path = None

        self._setup_variables()
        self._create_widgets()
        self._update_ui_for_mode()

    def _setup_variables(self):
        self.operation_mode_var = tk.StringVar(value='embed')
        self.audio_path_var = tk.StringVar(value="No audio file selected.")
        self.secret_file_path_var = tk.StringVar(value="No file selected.")
        self.plaintext_source_var = tk.StringVar(value='text_mode')
        self.random_start_var = tk.IntVar(value=1)
        self.encrypt_var = tk.IntVar(value=1)
        self.lsb_var = tk.StringVar(value="2")
        self.stego_key_var = tk.StringVar()

    def _create_widgets(self):
        frame_bg_color = self.style.lookup('TFrame', 'background')
        self.main_canvas = tk.Canvas(self.master, highlightthickness=0, background=frame_bg_color)
        scrollbar = ttk.Scrollbar(self.master, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = ttk.Frame(self.main_canvas, padding="20")
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.bind("<Configure>", self._reconfigure_canvas)
        self.main_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)
        def _on_mousewheel(event):
            self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        title_label = ttk.Label(self.scrollable_frame, text="Audio Steganography Tool", style='Header.TLabel')
        title_label.pack(pady=(0, 20), anchor='center')
        
        mode_frame = ttk.LabelFrame(self.scrollable_frame, text="Operation Mode", padding="10")
        mode_frame.pack(fill=tk.X, expand=True, pady=5)
        ttk.Radiobutton(mode_frame, text="Embed Message", variable=self.operation_mode_var, value='embed', command=self._update_ui_for_mode).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_frame, text="Extract Message", variable=self.operation_mode_var, value='extract', command=self._update_ui_for_mode).pack(side=tk.LEFT, padx=10)

        self.audio_frame = ttk.LabelFrame(self.scrollable_frame, text="1. Cover Audio File (*.mp3, *.wav)", padding="10")
        self.audio_frame.pack(fill=tk.X, expand=True, pady=10)
        ttk.Button(self.audio_frame, text="Browse...", command=self._select_audio_file).grid(row=0, column=0, padx=(0, 10))
        ttk.Label(self.audio_frame, textvariable=self.audio_path_var, wraplength=500).grid(row=0, column=1, sticky="ew")
        self.audio_frame.columnconfigure(1, weight=1)

        self.secret_frame = ttk.LabelFrame(self.scrollable_frame, text="2. Secret Message", padding="10")
        self.secret_frame.pack(fill=tk.X, expand=True, pady=10)
        ttk.Radiobutton(self.secret_frame, text="Text Input", variable=self.plaintext_source_var, value='text_mode').pack(anchor='w')
        text_container = ttk.Frame(self.secret_frame)
        text_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 10))
        text_scrollbar = ttk.Scrollbar(text_container)
        self.secret_text_input = tk.Text(text_container, height=5, width=60, font=('Courier', 10), relief=tk.SOLID, borderwidth=1, yscrollcommand=text_scrollbar.set)
        text_scrollbar.config(command=self.secret_text_input.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.secret_text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Radiobutton(self.secret_frame, text="File Input (any file type)", variable=self.plaintext_source_var, value='file_mode').pack(anchor='w', pady=(10, 0))
        file_input_container = ttk.Frame(self.secret_frame)
        file_input_container.pack(fill=tk.X, expand=True, padx=20)
        ttk.Button(file_input_container, text="Select Secret File...", command=self._select_secret_file).grid(row=0, column=0, padx=(0, 10))
        ttk.Label(file_input_container, textvariable=self.secret_file_path_var, wraplength=400).grid(row=0, column=1, sticky="ew")
        file_input_container.columnconfigure(1, weight=1)

        self.options_frame = ttk.LabelFrame(self.scrollable_frame, text="3. Configuration Options", padding="10")
        self.options_frame.pack(fill=tk.X, expand=True, pady=10)
        ttk.Label(self.options_frame, text="Encryption:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        encrypt_radios = ttk.Frame(self.options_frame)
        ttk.Radiobutton(encrypt_radios, text="Enable", variable=self.encrypt_var, value=1).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(encrypt_radios, text="Disable", variable=self.encrypt_var, value=0).pack(side=tk.LEFT, padx=5)
        encrypt_radios.grid(row=0, column=1, sticky='w')
        ttk.Label(self.options_frame, text="Start Point:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        random_radios = ttk.Frame(self.options_frame)
        ttk.Radiobutton(random_radios, text="Random", variable=self.random_start_var, value=1).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(random_radios, text="Sequential", variable=self.random_start_var, value=0).pack(side=tk.LEFT, padx=5)
        random_radios.grid(row=1, column=1, sticky='w')
        ttk.Label(self.options_frame, text="n-LSB:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        lsb_radios = ttk.Frame(self.options_frame)
        for i in range(1, 5):
            ttk.Radiobutton(lsb_radios, text=f"{i}-bit", variable=self.lsb_var, value=str(i)).pack(side=tk.LEFT, padx=5)
        lsb_radios.grid(row=2, column=1, sticky='w')
        
        self.key_frame = ttk.LabelFrame(self.scrollable_frame, text="Stego Key", padding="10")
        self.key_frame.pack(fill=tk.X, expand=True, pady=10)
        self.key_entry = ttk.Entry(self.key_frame, textvariable=self.stego_key_var, width=50, font=('Helvetica', 11), show="*")
        self.key_entry.pack(fill=tk.X, expand=True)

        audio_controls_frame = ttk.LabelFrame(self.scrollable_frame, text="Audio Controls", padding="10")
        audio_controls_frame.pack(fill=tk.X, expand=True, pady=10)
        audio_controls_frame.columnconfigure(1, weight=1)
        audio_controls_frame.columnconfigure(2, weight=1)
        ttk.Label(audio_controls_frame, text="Original Audio:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.play_orig_button = ttk.Button(audio_controls_frame, text="▶ Play", command=lambda: self._play_stop_audio('original'))
        self.play_orig_button.grid(row=0, column=1, sticky='ew', padx=5)
        self.download_orig_button = ttk.Button(audio_controls_frame, text="Download", command=lambda: self._download_audio('original'))
        self.download_orig_button.grid(row=0, column=2, sticky='ew', padx=5)
        ttk.Label(audio_controls_frame, text="Stego Audio:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.play_stego_button = ttk.Button(audio_controls_frame, text="▶ Play", command=lambda: self._play_stop_audio('stego'), state=tk.DISABLED)
        self.play_stego_button.grid(row=1, column=1, sticky='ew', padx=5)
        self.download_stego_button = ttk.Button(audio_controls_frame, text="Download", command=lambda: self._download_audio('stego'), state=tk.DISABLED)
        self.download_stego_button.grid(row=1, column=2, sticky='ew', padx=5)

        self.submit_button = ttk.Button(self.scrollable_frame, text="Embed Message", command=self._process_action, style='Submit.TButton', padding=10)
        self.submit_button.pack(pady=20, anchor='center')

    def _reconfigure_canvas(self, event=None):
        canvas_width = self.main_canvas.winfo_width()
        canvas_height = self.main_canvas.winfo_height()
        self.main_canvas.itemconfig(self.canvas_window, width=canvas_width)
        self.scrollable_frame.update_idletasks()
        frame_height = self.scrollable_frame.winfo_reqheight()
        if frame_height < canvas_height:
            new_y = (canvas_height - frame_height) // 2
            self.main_canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))
        else:
            new_y = 0
            self.main_canvas.configure(scrollregion=(0, 0, canvas_width, frame_height))
        self.main_canvas.coords(self.canvas_window, 0, new_y)

    def _execute_embed(self, audio_file, stego_key, n_lsb, use_encryption, use_random_start):
        secret_data = None
        secret_filename = ""
        if self.plaintext_source_var.get() == 'text_mode':
            secret_text = self.secret_text_input.get("1.0", "end-1c")
            if not secret_text:
                messagebox.showerror("Error", "Pesan rahasia tidak boleh kosong.")
                return
            secret_data = secret_text.encode('utf-8')
            secret_filename = "pesan.txt"
        else:
            secret_file = self.secret_file_path_var.get()
            if "No file selected" in secret_file or not os.path.exists(secret_file):
                messagebox.showerror("Error", "Silakan pilih file pesan rahasia yang valid.")
                return
            try:
                secret_filename = os.path.basename(secret_file)
                with open(secret_file, 'rb') as f:
                    secret_data = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"Gagal membaca file rahasia:\n{e}")
                return
        if not secret_data:
            messagebox.showerror("Error", "Data rahasia kosong.")
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".wav", filetypes=[("WAV files", "*.wav")], title="Simpan Audio Stego Sebagai...")
        if not output_path: return
        
        result = embed_message(
            cover_audio_path=audio_file, secret_data=secret_data, secret_filename=secret_filename,
            stego_key=stego_key, n_lsb=n_lsb, use_encryption=use_encryption, 
            use_random_start=use_random_start, output_path=output_path
        )
        if result['success']:
            self.stego_audio_path = result['output_path']
            self.play_stego_button.config(state=tk.NORMAL)
            self.download_stego_button.config(state=tk.NORMAL)
            info = (f"Data berhasil disisipkan!\n\n"
                    f"File Output: {os.path.basename(result['output_path'])}\n"
                    f"PSNR: {result.get('psnr', 'N/A'):.2f} dB\n"
                    f"Posisi Awal Payload: {result['starting_position']}\n"
                    f"Ukuran Data: {result.get('data_length_bytes', 'N/A')} bytes")
            messagebox.showinfo("Sukses", info)
        else:
            messagebox.showerror("Penyisipan Gagal", result['error'])
    
    def _play_stop_audio(self, audio_type):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.play_orig_button.config(text="▶ Play")
            self.play_stego_button.config(text="▶ Play")
            return
        path_to_play = None
        button_to_update = None
        if audio_type == 'original':
            path_to_play = self.audio_path_var.get()
            button_to_update = self.play_orig_button
        elif audio_type == 'stego':
            path_to_play = self.stego_audio_path
            button_to_update = self.play_stego_button
        if path_to_play and os.path.exists(path_to_play):
            try:
                pygame.mixer.music.load(path_to_play)
                pygame.mixer.music.play()
                self.is_playing = True
                button_to_update.config(text="■ Stop")
            except pygame.error as e:
                messagebox.showerror("Playback Error", f"Tidak dapat memutar file audio:\n{e}")
        else:
            messagebox.showwarning("File Not Found", "File audio tidak ditemukan.")

    def _download_audio(self, audio_type):
        source_path = None
        default_name = ""
        if audio_type == 'original':
            source_path = self.audio_path_var.get()
            default_name = "original_audio.mp3"
        elif audio_type == 'stego':
            source_path = self.stego_audio_path
            default_name = "stego_audio.wav"
        if source_path and os.path.exists(source_path):
            dest_path = filedialog.asksaveasfilename(
                initialfile=default_name,
                defaultextension=os.path.splitext(source_path)[1],
                filetypes=(("Audio Files", "*.wav *.mp3"), ("All files", "*.*"))
            )
            if dest_path:
                try:
                    shutil.copy(source_path, dest_path)
                    messagebox.showinfo("Success", f"File berhasil disimpan di:\n{dest_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Gagal menyimpan file:\n{e}")
        else:
            messagebox.showwarning("File Not Found", "File audio tidak ditemukan untuk diunduh.")

    def _select_audio_file(self):
        mode = self.operation_mode_var.get()
        if mode == 'embed':
            title = "Select Cover Audio File"
            filetypes = (("Audio files", "*.mp3 *.wav"),)
        else:
            title = "Select Stego WAV File"
            filetypes = (("WAV files", "*.wav"),)
        filepath = filedialog.askopenfilename(title=title, filetypes=filetypes)
        if filepath:
            self.audio_path_var.set(filepath)
            self.stego_audio_path = None
            self.play_stego_button.config(state=tk.DISABLED)
            self.download_stego_button.config(state=tk.DISABLED)
            if self.is_playing:
                pygame.mixer.music.stop()
                self.is_playing = False
                self.play_orig_button.config(text="▶ Play")

    def _select_secret_file(self):
        filepath = filedialog.askopenfilename(title="Select Secret Message File", filetypes=(("All files", "*.*"),))
        if filepath:
            self.secret_file_path_var.set(filepath)

    def _update_ui_for_mode(self):
        mode = self.operation_mode_var.get()
        if mode == 'embed':
            self.audio_frame.config(text="1. Cover Audio File (*.mp3, *.wav)")
            self.key_frame.config(text="4. Stego Key")
            self.secret_frame.pack(fill=tk.X, expand=True, pady=10)
            self.options_frame.pack(fill=tk.X, expand=True, pady=10)
            self.submit_button.config(text="Embed Message")
            
            self.secret_frame.pack_configure(before=self.options_frame)
            self.options_frame.pack_configure(before=self.key_frame)

        elif mode == 'extract':
            self.audio_frame.config(text="1. Stego Audio File (*.wav)")
            self.key_frame.config(text="2. Stego Key")
            self.secret_frame.pack_forget()
            self.options_frame.pack_forget()
            self.submit_button.config(text="Extract Message")
        
        self.master.update_idletasks()
        self._reconfigure_canvas()

    def _process_action(self):
        audio_file = self.audio_path_var.get()
        stego_key = self.stego_key_var.get()
        
        if "No audio file" in audio_file or not os.path.exists(audio_file):
            messagebox.showerror("Error", "Please select a valid audio file.")
            return
        if not stego_key:
            messagebox.showerror("Error", "Stego Key cannot be empty.")
            return
            
        mode = self.operation_mode_var.get()
        if mode == 'embed':
            n_lsb = int(self.lsb_var.get())
            use_encryption = bool(self.encrypt_var.get())
            use_random_start = bool(self.random_start_var.get())
            self._execute_embed(audio_file, stego_key, n_lsb, use_encryption, use_random_start)
        elif mode == 'extract':
            self._execute_extract(audio_file, stego_key)

    def _execute_extract(self, audio_file, stego_key):
        result = extract_message(
            stego_audio_path=audio_file,
            stego_key=stego_key
        )
        
        if result['success']:
            metadata = result['metadata']
            extracted_data = result['data']

            info = (f"Extraction Successful!\n\n"
                    f"--- Recovered File Details ---\n"
                    f"Original Filename: {metadata.get('filename', 'N/A')}\n"
                    f"File Size: {metadata.get('filesize', 'N/A')} bytes\n\n"
                    f"--- Embedding Parameters ---\n"
                    f"n-LSB Used: {metadata.get('n_lsb', 'N/A')}-bit\n"
                    f"Encryption: {'Enabled' if metadata.get('encrypted') else 'Disabled'}\n"
                    f"Start Point: {'Random' if metadata.get('random_start') else 'Sequential'}\n"
                    f"Payload Position: byte {result.get('starting_position', 'N/A')}\n\n"
                    "Do you want to save the extracted file?")
            
            save = messagebox.askyesno("Extraction Report", info)
            if save:
                output_path = filedialog.asksaveasfilename(
                    initialfile=metadata.get('filename', 'extracted_file'),
                    title="Save Extracted File..."
                )
                if output_path:
                    try:
                        with open(output_path, 'wb') as f:
                            f.write(extracted_data)
                        messagebox.showinfo("Success", f"File saved successfully at:\n{output_path}")
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to save file:\n{e}")
        else:
            messagebox.showerror("Extraction Failed", result['error'])

if __name__ == "__main__":
    root = tk.Tk()
    app = SteganographyApp(root)
    root.mainloop()