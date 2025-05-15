import numpy as np
from scipy import signal

class EqualizerFilter:
    def __init__(self):
        self.BAND1_RANGE = (80, 250)     
        self.BAND2_RANGE = (250, 500)    
        self.BAND3_RANGE = (500, 1000)   
        self.BAND4_RANGE = (1000, 2000)  
        self.BAND5_RANGE = (2000, 4000)  
        
        self.band_limits = [
            self.BAND1_RANGE,  
            self.BAND2_RANGE,  
            self.BAND3_RANGE,  
            self.BAND4_RANGE,  
            self.BAND5_RANGE  
        ]
        
        self.enabled = [True, True, True, True, True]
        
        self.filter_order = 4
        self.sample_rate = 16000  
    
    def set_filter_enabled(self, filter_idx, enabled):
        if 0 <= filter_idx < 5:
            self.enabled[filter_idx] = enabled
    
    def is_filter_enabled(self, filter_idx):
        if 0 <= filter_idx < 5:
            return self.enabled[filter_idx]
        return False
    
    def apply_filter(self, input_signal, filter_idx, sample_rate=None):
        if sample_rate is None:
            sample_rate = self.sample_rate
        else:
            self.sample_rate = sample_rate
            
        if not (0 <= filter_idx < 5) or not self.enabled[filter_idx]:
            return np.zeros_like(input_signal)
            
        low_freq, high_freq = self.band_limits[filter_idx]
        
        nyquist = sample_rate / 2.0
        
        if low_freq >= nyquist:
            return np.zeros_like(input_signal)
            
        high_freq = min(high_freq, nyquist * 0.99)
        
        low_norm = low_freq / nyquist
        high_norm = high_freq / nyquist
        
        low_norm = max(low_norm, 0.001)
        high_norm = min(high_norm, 0.999)
        
        if high_norm <= low_norm:
            high_norm = low_norm + 0.001
            if high_norm >= 0.999:
                return input_signal if filter_idx == 2 else np.zeros_like(input_signal)
        
        b, a = signal.butter(self.filter_order, [low_norm, high_norm], btype='bandpass')
        
        filtered_signal = signal.filtfilt(b, a, input_signal)
        
        return filtered_signal
    
    def set_sample_rate(self, rate):
        self.sample_rate = rate 