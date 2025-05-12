import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class EqualizerUI:
    # Definición de colores como constantes
    COLOR_INPUT_SIGNAL = 'blue'              # Color señal de entrada principal
    COLOR_INPUT_COMPONENTS = ['#ff7f0e', '#2ca02c', '#d62728']  # Colores para cada componente
    COLOR_OUTPUT_SIGNAL = 'red'              # Color señal de salida
    COLOR_COMPONENT_ALPHA = 0.5              # Transparencia de las componentes
    COLOR_GRID = '#cccccc'                   # Color de la cuadrícula
    
    def __init__(self, root, signal_generator, equalizer_filter, signal_mixer):
        self.root = root
        self.root.title("5-Band Equalizer")
        self.root.geometry("1700x900")  # Aumentado el tamaño de la ventana
        
        self.signal_generator = signal_generator
        self.equalizer_filter = equalizer_filter
        self.signal_mixer = signal_mixer
        
        # Set all filter gains to 1.0 (fixed)
        for i in range(5):
            self.signal_mixer.set_filter_gain(i, 1.0)
        
        # Duration of signal to display
        self.duration = 1.0  # 1 second
        
        # Create UI elements
        self._create_layout()
        
        # Initial signal generation and display
        self.update_display()
        
    def _create_layout(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Controls frame (top)
        controls_frame = ttk.Frame(main_frame)
        controls_frame.pack(fill=tk.X, expand=False, padx=5, pady=5)
        
        # Plots frame (bottom)
        plots_frame = ttk.Frame(main_frame)
        plots_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Split controls into left and right
        left_controls = ttk.Frame(controls_frame)
        left_controls.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        right_controls = ttk.Frame(controls_frame)
        right_controls.pack(side=tk.RIGHT, fill=tk.X, expand=True)
        
        # ------ CONTROLS ------
        # Signal Generator Controls
        generator_frame = ttk.LabelFrame(left_controls, text="Signal Generator")
        generator_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create sliders for each component
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
            
            # Create value label for frequency
            freq_value_label = ttk.Label(freq_frame, text=f"{self.signal_generator.frequencies[i]:.1f} Hz")
            freq_value_label.pack(side=tk.RIGHT, padx=5)
            self.freq_value_labels.append(freq_value_label)
            
            # Create frequency slider with callback
            freq_slider = ttk.Scale(
                freq_frame, 
                from_=1, 
                to=500, # Aumentado a 500 Hz
                orient=tk.HORIZONTAL,
                command=lambda value, idx=i: self.update_freq_value(value, idx)
            )
            freq_slider.set(self.signal_generator.frequencies[i])
            freq_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.freq_sliders.append(freq_slider)
            
            amp_frame = ttk.Frame(comp_frame)
            amp_frame.pack(fill=tk.X, pady=2)
            ttk.Label(amp_frame, text="Amplitude:").pack(side=tk.LEFT)
            
            # Create value label for amplitude
            amp_value_label = ttk.Label(amp_frame, text=f"{self.signal_generator.amplitudes[i]:.2f}")
            amp_value_label.pack(side=tk.RIGHT, padx=5)
            self.amp_value_labels.append(amp_value_label)
            
            # Create amplitude slider with callback
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
        
        # Filter Controls
        filter_frame = ttk.LabelFrame(right_controls, text="Equalizer Bands")
        filter_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Filter checkboxes and labels
        self.filter_vars = []
        filter_labels = ["Banda 1 (0-100 Hz)", "Banda 2 (101-200 Hz)", 
                        "Banda 3 (201-300 Hz)", "Banda 4 (301-400 Hz)", 
                        "Banda 5 (401-500 Hz)"]
        
        for i in range(5):
            filter_var = tk.BooleanVar(value=True)
            self.filter_vars.append(filter_var)
            
            # Check button for filter enable/disable
            filter_check = ttk.Checkbutton(
                filter_frame, 
                text=filter_labels[i],
                variable=filter_var,
                command=self.update_filters
            )
            filter_check.pack(anchor=tk.W, padx=5, pady=5)
        
        # ------ PLOTS ------
        # All plots in a single horizontal row
        plots_row = ttk.Frame(plots_frame)
        plots_row.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Time Domain Plot for Input Signal
        input_time_frame = ttk.LabelFrame(plots_row, text="Input Signal - Time Domain")
        input_time_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.input_time_fig = Figure(figsize=(4, 4), dpi=100)
        self.input_time_canvas = FigureCanvasTkAgg(self.input_time_fig, master=input_time_frame)
        self.input_time_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Frequency Domain Plot for Input Signal
        input_freq_frame = ttk.LabelFrame(plots_row, text="Input Signal - Frequency Domain")
        input_freq_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.input_freq_fig = Figure(figsize=(4, 4), dpi=100)
        self.input_freq_canvas = FigureCanvasTkAgg(self.input_freq_fig, master=input_freq_frame)
        self.input_freq_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Time Domain Plot for Output Signal
        output_time_frame = ttk.LabelFrame(plots_row, text="Output Signal - Time Domain")
        output_time_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.output_time_fig = Figure(figsize=(4, 4), dpi=100)
        self.output_time_canvas = FigureCanvasTkAgg(self.output_time_fig, master=output_time_frame)
        self.output_time_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
        
        # Frequency Domain Plot for Output Signal
        output_freq_frame = ttk.LabelFrame(plots_row, text="Output Signal - Frequency Domain")
        output_freq_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=2)
        
        self.output_freq_fig = Figure(figsize=(4, 4), dpi=100)
        self.output_freq_canvas = FigureCanvasTkAgg(self.output_freq_fig, master=output_freq_frame)
        self.output_freq_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=3, pady=3)
    
    def update_freq_value(self, value, index):
        """Update frequency value label when slider is moved"""
        freq_value = float(value)
        self.freq_value_labels[index].config(text=f"{freq_value:.1f} Hz")
        
        # Actualizar el generador de señal con el nuevo valor
        self.signal_generator.set_component_parameters(
            index,
            frequency=freq_value
        )
        
        # Actualizar las gráficas
        self.update_display()
    
    def update_amp_value(self, value, index):
        """Update amplitude value label when slider is moved"""
        amp_value = float(value)
        self.amp_value_labels[index].config(text=f"{amp_value:.2f}")
        
        # Actualizar el generador de señal con el nuevo valor
        self.signal_generator.set_component_parameters(
            index,
            amplitude=amp_value
        )
        
        # Actualizar las gráficas
        self.update_display()
    
    def update_filters(self):
        # Update filter states from UI
        for i in range(5):
            self.equalizer_filter.set_filter_enabled(i, self.filter_vars[i].get())
        
        # Update display
        self.update_display()
    
    def compute_fft(self, signal, sample_rate):
        """Compute FFT for the given signal"""
        # Calculate FFT
        fft_result = np.fft.rfft(signal)
        fft_freq = np.fft.rfftfreq(len(signal), 1/sample_rate)
        fft_magnitude = np.abs(fft_result) / len(signal) * 2  # Normalized magnitude
        
        # Limit to max frequency of interest (500Hz)
        max_freq_idx = np.where(fft_freq <= 500)[0][-1] + 1
        return fft_freq[:max_freq_idx], fft_magnitude[:max_freq_idx]
    
    def update_display(self):
        # Generate input signal
        input_signal, time_axis = self.signal_generator.generate_complete_signal(self.duration)
        sample_rate = self.signal_generator.get_sample_rate()
        
        # Apply filters
        filtered_signals = []
        for i in range(5):
            filtered = self.equalizer_filter.apply_filter(
                input_signal, 
                i, 
                self.signal_generator.get_sample_rate()
            )
            filtered_signals.append(filtered)
        
        # Mix filtered signals
        output_signal = self.signal_mixer.mix_signals(
            filtered_signals,
            [self.filter_vars[i].get() for i in range(5)]
        )
        
        # Calculate FFT for input and output signals
        input_fft_freq, input_fft_mag = self.compute_fft(input_signal, sample_rate)
        output_fft_freq, output_fft_mag = self.compute_fft(output_signal, sample_rate)
        
        # Update input signal time domain plot
        self.input_time_fig.clear()
        ax_input_time = self.input_time_fig.add_subplot(111)
        ax_input_time.plot(time_axis, input_signal, color=self.COLOR_INPUT_SIGNAL, label='Complete Signal')
        
        # Also plot individual components
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
        
        # Update input signal frequency domain plot
        self.input_freq_fig.clear()
        ax_input_freq = self.input_freq_fig.add_subplot(111)
        ax_input_freq.plot(input_fft_freq, input_fft_mag, color=self.COLOR_INPUT_SIGNAL)
        
        # Also plot component FFTs
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
        ax_input_freq.set_xlim(0, 500)  # Limit to our frequency range of interest
        ax_input_freq.legend()
        ax_input_freq.grid(True, color=self.COLOR_GRID)
        
        # Update output signal time domain plot
        self.output_time_fig.clear()
        ax_output_time = self.output_time_fig.add_subplot(111)
        ax_output_time.plot(time_axis, output_signal, color=self.COLOR_OUTPUT_SIGNAL, label='Equalized Signal')
        
        ax_output_time.set_xlabel('Time (s)')
        ax_output_time.set_ylabel('Amplitude')
        ax_output_time.set_title('Output Signal - Time Domain')
        ax_output_time.legend()
        ax_output_time.grid(True, color=self.COLOR_GRID)
        
        # Update output signal frequency domain plot
        self.output_freq_fig.clear()
        ax_output_freq = self.output_freq_fig.add_subplot(111)
        ax_output_freq.plot(output_fft_freq, output_fft_mag, color=self.COLOR_OUTPUT_SIGNAL, label='Equalized Signal')
        
        ax_output_freq.set_xlabel('Frequency (Hz)')
        ax_output_freq.set_ylabel('Magnitude')
        ax_output_freq.set_title('Output Signal - Frequency Domain')
        ax_output_freq.set_xlim(0, 500)  # Limit to our frequency range of interest
        ax_output_freq.legend()
        ax_output_freq.grid(True, color=self.COLOR_GRID)
        
        # Refresh canvases
        self.input_time_canvas.draw()
        self.input_freq_canvas.draw()
        self.output_time_canvas.draw()
        self.output_freq_canvas.draw()
        
    def run(self):
        """Run the UI main loop"""
        self.root.mainloop() 