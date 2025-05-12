import numpy as np

class SignalGenerator:
    def __init__(self):
        # Constantes de frecuencia
        self.MAX_FREQUENCY = 500  # Hz - Máxima frecuencia permitida
        self.DEFAULT_FREQUENCIES = [5, 15, 30]  # Hz
        self.DEFAULT_AMPLITUDES = [1.0, 0.7, 0.5]
        
        # Default parameters for the three sinusoidal components
        self.frequencies = self.DEFAULT_FREQUENCIES.copy()
        self.amplitudes = self.DEFAULT_AMPLITUDES.copy()
        self.phases = [0, 0, 0]  # Radians
        self.sample_rate = 2000  # Hz - Increased to support higher frequencies
        
    def set_component_parameters(self, component_idx, frequency=None, amplitude=None, phase=None):
        """Set parameters for a specific component"""
        if 0 <= component_idx < 3:
            if frequency is not None:
                # Ensure frequency is less than Nyquist frequency (sample_rate/2)
                # max_freq = min(self.MAX_FREQUENCY, self.sample_rate / 2.0 * 0.95)  # 95% of Nyquist as a safety margin
                # self.frequencies[component_idx] = min(float(frequency), max_freq)
                self.frequencies[component_idx] = frequency
            if amplitude is not None:
                self.amplitudes[component_idx] = amplitude
            if phase is not None:
                self.phases[component_idx] = phase
    
    def generate_component(self, component_idx, duration):
        """Generate a single component of the signal"""
        if 0 <= component_idx < 3:
            t = np.linspace(0, duration, int(duration * self.sample_rate), endpoint=False)
            return self.amplitudes[component_idx] * np.sin(
                2 * np.pi * self.frequencies[component_idx] * t + self.phases[component_idx]
            ), t
        return np.array([]), np.array([])
    
    def generate_complete_signal(self, duration):
        """Generate the complete signal with all three components"""
        t = np.linspace(0, duration, int(duration * self.sample_rate), endpoint=False)
        signal = np.zeros_like(t)
        
        # Add each component to the signal
        for i in range(3):
            signal += self.amplitudes[i] * np.sin(
                2 * np.pi * self.frequencies[i] * t + self.phases[i]
            )
            
        return signal, t
    
    def get_sample_rate(self):
        """Return the sample rate"""
        return self.sample_rate
    
    def set_sample_rate(self, rate):
        """Set the sample rate"""
        if rate > 0:
            self.sample_rate = rate
            
            # Update frequencies to ensure they're below Nyquist
            nyquist = rate / 2.0
            for i in range(3):
                if self.frequencies[i] >= nyquist:
                    self.frequencies[i] = nyquist * 0.95 