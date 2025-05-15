import numpy as np

class SignalGenerator:
    def __init__(self):
        self.MAX_FREQUENCY = 4000  
        self.DEFAULT_FREQUENCIES = [150, 300, 800]  
        self.DEFAULT_AMPLITUDES = [1.0, 0.7, 0.5]
        
        self.frequencies = self.DEFAULT_FREQUENCIES.copy()
        self.amplitudes = self.DEFAULT_AMPLITUDES.copy()
        self.phases = [0, 0, 0]  
        self.sample_rate = 16000  
        
    def set_component_parameters(self, component_idx, frequency=None, amplitude=None, phase=None):
        if 0 <= component_idx < 3:
            if frequency is not None:
                max_freq = min(self.MAX_FREQUENCY, self.sample_rate / 2.0 * 0.95)  
                self.frequencies[component_idx] = min(float(frequency), max_freq)
            if amplitude is not None:
                self.amplitudes[component_idx] = amplitude
            if phase is not None:
                self.phases[component_idx] = phase
    
    def generate_component(self, component_idx, duration):
        if 0 <= component_idx < 3:
            t = np.linspace(0, duration, int(duration * self.sample_rate), endpoint=False)
            return self.amplitudes[component_idx] * np.sin(
                2 * np.pi * self.frequencies[component_idx] * t + self.phases[component_idx]
            ), t
        return np.array([]), np.array([])
    
    def generate_complete_signal(self, duration):
        t = np.linspace(0, duration, int(duration * self.sample_rate), endpoint=False)
        signal = np.zeros_like(t)
        
        for i in range(3):
            signal += self.amplitudes[i] * np.sin(
                2 * np.pi * self.frequencies[i] * t + self.phases[i]
            )
            
        return signal, t
    
    def get_sample_rate(self):
        return self.sample_rate
    
    def set_sample_rate(self, rate):
        if rate > 0:
            self.sample_rate = rate
            
            nyquist = rate / 2.0
            for i in range(3):
                if self.frequencies[i] >= nyquist:
                    self.frequencies[i] = nyquist * 0.95 