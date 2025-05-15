import tkinter as tk
from tkinter import ttk, filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import scipy.io.wavfile as wavfile
import pyaudio
import threading
import time

class EqualizerUI:
    COLOR_INPUT_SIGNAL = 'blue'              
    COLOR_INPUT_COMPONENTS = ['#ff7f0e', '#2ca02c', '#d62728']  
    COLOR_OUTPUT_SIGNAL = 'red'              
    COLOR_COMPONENT_ALPHA = 0.5              
    COLOR_GRID = '#cccccc'                   
    
    def __init__(self, root, signal_generator, equalizer_filter, signal_mixer):
        self.root = root
        self.root.title("5-Band Equalizer")
        self.root.geometry("1700x950")  
        
        self.signal_generator = signal_generator
        self.equalizer_filter = equalizer_filter
        self.signal_mixer = signal_mixer
        
        self.filter_vars = []
        for i in range(5):
            self.filter_vars.append(tk.BooleanVar(value=True))
        
        for i in range(5):
            self.signal_mixer.set_filter_gain(i, 1.0)
        
        self.duration = 1.0  
        
        self.input_time_fig = None
        self.input_freq_fig = None
        self.output_time_fig = None
        self.output_freq_fig = None
        self.input_time_canvas = None
        self.input_freq_canvas = None
        self.output_time_canvas = None
        self.output_freq_canvas = None
        
        self.is_playing = False
        self.audio_thread = None
        self.stream = None
        self.pyaudio_instance = None
        self.current_audio_data = None
        self.sample_rate = 44100
        
        self.wav_file_path = None
        self.wav_data = None
        self.use_wav = tk.BooleanVar(value=False)
        
        self._create_layout()
        
        self.update_display()
        
    def _create_layout(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        plots_frame = ttk.Frame(main_frame)
        plots_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        playback_frame = ttk.LabelFrame(main_frame, text="Reproducción de Audio")
        playback_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        left_controls = ttk.Frame(controls_frame)
        left_controls.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        right_controls = ttk.Frame(controls_frame)
        right_controls.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # ------ CONTROLS ------
        generator_frame = ttk.LabelFrame(left_controls, text="Signal Generator")
        generator_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.freq_sliders = []
        self.amp_sliders = []
        self.freq_value_labels = []
        self.amp_value_labels = []
        
        for i in range(3):
            comp_frame = ttk.Frame(generator_frame)
            comp_frame.pack(fill=tk.X, padx=5, pady=5)
            
            ttk.Label(comp_frame, text=f"Component {i+1}").pack(anchor=tk.W)
            
            freq_frame = ttk.Frame(comp_frame)
            freq_frame.pack(fill=tk.X, pady=2)
            ttk.Label(freq_frame, text="Frequency (Hz):").pack(side=tk.LEFT)
            
            freq_value_label = ttk.Label(freq_frame, text=f"{self.signal_generator.frequencies[i]:.1f} Hz")
            freq_value_label.pack(side=tk.RIGHT, padx=5)
            self.freq_value_labels.append(freq_value_label)
            
            freq_slider = ttk.Scale(
                freq_frame, 
                from_=80, 
                to=4000, 
                orient=tk.HORIZONTAL,
                command=lambda value, idx=i: self.update_freq_value(value, idx)
            )
            freq_slider.set(self.signal_generator.frequencies[i])
            freq_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.freq_sliders.append(freq_slider)
            
            amp_frame = ttk.Frame(comp_frame)
            amp_frame.pack(fill=tk.X, pady=2)
            ttk.Label(amp_frame, text="Amplitude:").pack(side=tk.LEFT)
            
            amp_value_label = ttk.Label(amp_frame, text=f"{self.signal_generator.amplitudes[i]:.2f}")
            amp_value_label.pack(side=tk.RIGHT, padx=5)
            self.amp_value_labels.append(amp_value_label)
            
            amp_slider = ttk.Scale(
                amp_frame, 
                from_=0, 
                to=2, 
                orient=tk.HORIZONTAL,
                command=lambda value, idx=i: self.update_amp_value(value, idx)
            )
            amp_slider.set(self.signal_generator.amplitudes[i])
            amp_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.amp_sliders.append(amp_slider)
        
        wav_frame = ttk.Frame(generator_frame)
        wav_frame.pack(fill=tk.X, padx=5, pady=10)
        
        wav_check = ttk.Checkbutton(
            wav_frame,
            text="Usar archivo WAV en lugar de señal generada",
            variable=self.use_wav,
            command=self.toggle_wav_mode
        )
        wav_check.pack(anchor=tk.W, padx=5, pady=5)
        
        self.browse_button = ttk.Button(
            wav_frame,
            text="Seleccionar archivo WAV",
            command=self.browse_wav_file,
            state="disabled"
        )
        self.browse_button.pack(anchor=tk.W, padx=5, pady=5)
        
        self.wav_file_label = ttk.Label(wav_frame, text="No hay archivo seleccionado")
        self.wav_file_label.pack(anchor=tk.W, padx=5, pady=5)
        
        filter_frame = ttk.LabelFrame(right_controls, text="Equalizer Bands")
        filter_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        filter_labels = ["Banda 1 (80-250 Hz): Voz masculina", 
                        "Banda 2 (250-500 Hz): Voz femenina", 
                        "Banda 3 (500-1000 Hz): Primer formante", 
                        "Banda 4 (1000-2000 Hz): Segundo formante", 
                        "Banda 5 (2000-4000 Hz): Armónicos altos"]
        
        for i in range(5):
            filter_check = ttk.Checkbutton(
                filter_frame, 
                text=filter_labels[i],
                variable=self.filter_vars[i],
                command=self.update_filters
            )
            filter_check.pack(anchor=tk.W, padx=5, pady=5)
        
        # ------ PLOTS ------
        plots_row = ttk.Frame(plots_frame)
        plots_row.pack(fill=tk.BOTH, expand=True, pady=5)
        
        input_time_frame = ttk.LabelFrame(plots_row, text="Input Signal - Time Domain")
        input_time_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.input_time_fig = Figure(figsize=(4, 4), dpi=100)
        self.input_time_canvas = FigureCanvasTkAgg(self.input_time_fig, master=input_time_frame)
        self.input_time_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        input_freq_frame = ttk.LabelFrame(plots_row, text="Input Signal - Frequency Domain")
        input_freq_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.input_freq_fig = Figure(figsize=(4, 4), dpi=100)
        self.input_freq_canvas = FigureCanvasTkAgg(self.input_freq_fig, master=input_freq_frame)
        self.input_freq_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        output_time_frame = ttk.LabelFrame(plots_row, text="Output Signal - Time Domain")
        output_time_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.output_time_fig = Figure(figsize=(4, 4), dpi=100)
        self.output_time_canvas = FigureCanvasTkAgg(self.output_time_fig, master=output_time_frame)
        self.output_time_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        output_freq_frame = ttk.LabelFrame(plots_row, text="Output Signal - Frequency Domain")
        output_freq_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.output_freq_fig = Figure(figsize=(4, 4), dpi=100)
        self.output_freq_canvas = FigureCanvasTkAgg(self.output_freq_fig, master=output_freq_frame)
        self.output_freq_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # ------ PLAYBACK CONTROLS ------
        playback_buttons_frame = ttk.Frame(playback_frame)
        playback_buttons_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.play_button = ttk.Button(
            playback_buttons_frame, 
            text="▶ Reproducir", 
            command=self.play_audio
        )
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        self.pause_button = ttk.Button(
            playback_buttons_frame, 
            text="⏸ Pausar", 
            command=self.pause_audio,
            state="disabled"
        )
        self.pause_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(
            playback_buttons_frame, 
            text="⏹ Detener", 
            command=self.stop_audio,
            state="disabled"
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        self.status_label = ttk.Label(playback_frame, text="Listo para reproducir")
        self.status_label.pack(anchor=tk.W, padx=5, pady=5)
    
    def toggle_wav_mode(self):
        """Toggle between generated signal and WAV file modes"""
        if self.use_wav.get():
            self.browse_button.config(state="normal")
            for slider in self.freq_sliders + self.amp_sliders:
                slider.config(state="disabled")
        else:
            self.browse_button.config(state="disabled")
            for slider in self.freq_sliders + self.amp_sliders:
                slider.config(state="normal")
        
        self.update_display()
    
    def browse_wav_file(self):
        """Open file dialog to select a WAV file"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo WAV",
            filetypes=[("WAV files", "*.wav")]
        )
        
        if file_path:
            self.wav_file_path = file_path
            self.wav_file_label.config(text=f"Archivo: {file_path.split('/')[-1]}")
            self.load_wav_file()
            self.update_display()
    
    def load_wav_file(self):
        """Load the selected WAV file"""
        try:
            self.sample_rate, wav_data = wavfile.read(self.wav_file_path)
            
            if len(wav_data.shape) > 1: 
                wav_data = np.mean(wav_data, axis=1)
            
            wav_data = wav_data.astype(np.float32)
            if np.max(np.abs(wav_data)) > 0:
                wav_data = wav_data / np.max(np.abs(wav_data))
            
            self.wav_data = wav_data
            self.status_label.config(text=f"Archivo WAV cargado: {self.sample_rate} Hz")
            return True
        except Exception as e:
            self.status_label.config(text=f"Error al cargar archivo WAV: {str(e)}")
            self.wav_data = None
            return False
    
    def update_freq_value(self, value, index):
        """Update frequency value label when slider is moved"""
        freq_value = float(value)
        self.freq_value_labels[index].config(text=f"{freq_value:.1f} Hz")
        
        self.signal_generator.set_component_parameters(
            index,
            frequency=freq_value
        )
        
        self.update_display()
    
    def update_amp_value(self, value, index):
        """Update amplitude value label when slider is moved"""
        amp_value = float(value)
        self.amp_value_labels[index].config(text=f"{amp_value:.2f}")
        
        self.signal_generator.set_component_parameters(
            index,
            amplitude=amp_value
        )
        
        self.update_display()
    
    def update_filters(self):
        for i in range(5):
            self.equalizer_filter.set_filter_enabled(i, self.filter_vars[i].get())
        
        self.update_display()
    
    def compute_fft(self, signal, sample_rate):
        """Compute FFT for the given signal"""
        fft_result = np.fft.rfft(signal)
        fft_freq = np.fft.rfftfreq(len(signal), 1/sample_rate)
        fft_magnitude = np.abs(fft_result) / len(signal) * 2  
        
        max_freq_idx = np.where(fft_freq <= 4000)[0][-1] + 1
        return fft_freq[:max_freq_idx], fft_magnitude[:max_freq_idx]
    
    def update_display(self):
        if self.input_time_fig is None:
            return
            
        if self.use_wav.get() and self.wav_data is not None:
            max_samples = min(self.sample_rate, len(self.wav_data))
            input_signal = self.wav_data[:max_samples]
            time_axis = np.linspace(0, max_samples/self.sample_rate, max_samples)
            sample_rate = self.sample_rate
        else:
            input_signal, time_axis = self.signal_generator.generate_complete_signal(self.duration)
            sample_rate = self.signal_generator.get_sample_rate()
        
        filtered_signals = []
        for i in range(5):
            filtered = self.equalizer_filter.apply_filter(
                input_signal, 
                i, 
                sample_rate
            )
            filtered_signals.append(filtered)
        
        output_signal = self.signal_mixer.mix_signals(
            filtered_signals,
            [self.filter_vars[i].get() for i in range(5)]
        )
        
        self.current_audio_data = output_signal
        
        input_fft_freq, input_fft_mag = self.compute_fft(input_signal, sample_rate)
        output_fft_freq, output_fft_mag = self.compute_fft(output_signal, sample_rate)
        
        self.input_time_fig.clear()
        ax_input_time = self.input_time_fig.add_subplot(111)
        ax_input_time.plot(time_axis, input_signal, color=self.COLOR_INPUT_SIGNAL, label='Input Signal')
        
        if not self.use_wav.get():
            for i in range(3):
                component, _ = self.signal_generator.generate_component(i, self.duration)
                ax_input_time.plot(time_axis, component, '--', 
                                color=self.COLOR_INPUT_COMPONENTS[i], 
                                alpha=self.COLOR_COMPONENT_ALPHA, 
                                label=f'Component {i+1}')
        
        ax_input_time.set_xlabel('Time (s)')
        ax_input_time.set_ylabel('Amplitude')
        ax_input_time.set_title('Input Signal - Time Domain')
        ax_input_time.legend()
        ax_input_time.grid(True, color=self.COLOR_GRID)
        
        self.input_freq_fig.clear()
        ax_input_freq = self.input_freq_fig.add_subplot(111)
        ax_input_freq.plot(input_fft_freq, input_fft_mag, color=self.COLOR_INPUT_SIGNAL)
        
        if not self.use_wav.get():
            for i in range(3):
                component, _ = self.signal_generator.generate_component(i, self.duration)
                comp_fft_freq, comp_fft_mag = self.compute_fft(component, sample_rate)
                ax_input_freq.plot(comp_fft_freq, comp_fft_mag, '--', 
                                color=self.COLOR_INPUT_COMPONENTS[i], 
                                alpha=self.COLOR_COMPONENT_ALPHA, 
                                label=f'Component {i+1}')
        
        ax_input_freq.set_xlabel('Frequency (Hz)')
        ax_input_freq.set_ylabel('Magnitude')
        ax_input_freq.set_title('Input Signal - Frequency Domain')
        ax_input_freq.set_xlim(0, 4000)  
        ax_input_freq.legend()
        ax_input_freq.grid(True, color=self.COLOR_GRID)
        
        self.output_time_fig.clear()
        ax_output_time = self.output_time_fig.add_subplot(111)
        ax_output_time.plot(time_axis, output_signal, color=self.COLOR_OUTPUT_SIGNAL, label='Equalized Signal')
        
        ax_output_time.set_xlabel('Time (s)')
        ax_output_time.set_ylabel('Amplitude')
        ax_output_time.set_title('Output Signal - Time Domain')
        ax_output_time.legend()
        ax_output_time.grid(True, color=self.COLOR_GRID)
        
        self.output_freq_fig.clear()
        ax_output_freq = self.output_freq_fig.add_subplot(111)
        ax_output_freq.plot(output_fft_freq, output_fft_mag, color=self.COLOR_OUTPUT_SIGNAL, label='Equalized Signal')
        
        ax_output_freq.set_xlabel('Frequency (Hz)')
        ax_output_freq.set_ylabel('Magnitude')
        ax_output_freq.set_title('Output Signal - Frequency Domain')
        ax_output_freq.set_xlim(0, 4000)  
        ax_output_freq.legend()
        ax_output_freq.grid(True, color=self.COLOR_GRID)
        
        self.input_time_canvas.draw()
        self.input_freq_canvas.draw()
        self.output_time_canvas.draw()
        self.output_freq_canvas.draw()
    
    def play_audio(self):
        """Play the equalized audio"""
        if self.is_playing or self.current_audio_data is None:
            return
        
        self.is_playing = True
        self.status_label.config(text="Reproduciendo...")
        self.play_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self.stop_button.config(state="normal")
        
        self.audio_thread = threading.Thread(target=self._audio_playback_thread)
        self.audio_thread.daemon = True
        self.audio_thread.start()
        
    def pause_audio(self):
        """Pause the audio playback"""
        if not self.is_playing:
            return
        
        self.is_playing = False
        self.status_label.config(text="Pausado")
        self.play_button.config(state="normal")
        self.pause_button.config(state="disabled")
    
    def stop_audio(self):
        """Stop the audio playback"""
        self.is_playing = False
        self.status_label.config(text="Detenido")
        self.play_button.config(state="normal")
        self.pause_button.config(state="disabled")
        self.stop_button.config(state="disabled")
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None
    
    def _audio_playback_thread(self):
        """Thread function for audio playback"""
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            
            if self.use_wav.get() and self.wav_data is not None:
                sample_rate = self.sample_rate
            else:
                sample_rate = self.signal_generator.get_sample_rate()
            
            audio_data = self.current_audio_data.copy()
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data)) * 0.9
            
            audio_data = audio_data.astype(np.float32)
            
            def audio_callback(in_data, frame_count, time_info, status):
                if not self.is_playing:
                    return (np.zeros(frame_count, dtype=np.float32), pyaudio.paComplete)
                
                if hasattr(self, 'playback_position'):
                    pos = self.playback_position
                else:
                    pos = 0
                    self.playback_position = 0
                
                if pos >= len(audio_data):
                    self.root.after(100, self.stop_audio)
                    return (np.zeros(frame_count, dtype=np.float32), pyaudio.paComplete)
                
                chunk = audio_data[pos:min(pos+frame_count, len(audio_data))]
                self.playback_position += len(chunk)
                
                if len(chunk) < frame_count:
                    chunk = np.pad(chunk, (0, frame_count - len(chunk)), 'constant')
                
                return (chunk, pyaudio.paContinue)
            
            self.stream = self.pyaudio_instance.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=int(sample_rate),
                output=True,
                stream_callback=audio_callback
            )
            
            self.playback_position = 0
            self.stream.start_stream()
            
            while self.stream.is_active() and self.is_playing:
                time.sleep(0.1)
            
            if self.is_playing:
                self.root.after(0, self.stop_audio)
                
        except Exception as e:
            self.status_label.config(text=f"Error de reproducción: {str(e)}")
            self.root.after(0, self.stop_audio)
    
    def run(self):
        """Run the UI main loop"""
        self.root.mainloop()
        
    def __del__(self):
        """Cleanup resources on destroy"""
        self.stop_audio() 