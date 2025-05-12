import numpy as np
from scipy import signal

class EqualizerFilter:
    def __init__(self):
        # Define frequency bands as constants for easy modification
        self.BAND1_RANGE = (0, 100)     # Low band
        self.BAND2_RANGE = (101, 200)   # Low-mid band
        self.BAND3_RANGE = (201, 300)   # Mid band
        self.BAND4_RANGE = (301, 400)   # Mid-high band
        self.BAND5_RANGE = (401, 500)   # High band
        
        # Define 5 frequency bands (in Hz)
        self.band_limits = [
            self.BAND1_RANGE,  # Band 1
            self.BAND2_RANGE,  # Band 2
            self.BAND3_RANGE,  # Band 3
            self.BAND4_RANGE,  # Band 4
            self.BAND5_RANGE   # Band 5
        ]
        
        # Filter states
        self.enabled = [True, True, True, True, True]
        
        # Default filter parameters
        self.filter_order = 4
        self.sample_rate = 1000  # Hz
    
    def set_filter_enabled(self, filter_idx, enabled):
        """Enable or disable a specific filter"""
        if 0 <= filter_idx < 5:
            self.enabled[filter_idx] = enabled
    
    def is_filter_enabled(self, filter_idx):
        """Check if a filter is enabled"""
        if 0 <= filter_idx < 5:
            return self.enabled[filter_idx]
        return False
    
    def apply_filter(self, input_signal, filter_idx, sample_rate=None):
        """Apply a specific filter to the input signal"""
        if sample_rate is None:
            sample_rate = self.sample_rate
        else:
            self.sample_rate = sample_rate
            
        if not (0 <= filter_idx < 5) or not self.enabled[filter_idx]:
            return np.zeros_like(input_signal)
            
        # Get band limits
        low_freq, high_freq = self.band_limits[filter_idx]
        
        # Check if the frequency band is valid for current sample rate
        nyquist = sample_rate / 2.0
        
        # Handle special cases where frequencies are too high for the sample rate
        if low_freq >= nyquist:
            # If both frequencies are above Nyquist, return zeros
            return np.zeros_like(input_signal)
            
        # Ensure high_freq is below Nyquist
        high_freq = min(high_freq, nyquist * 0.99)
        
        # Normalize frequencies to Nyquist frequency
        low_norm = low_freq / nyquist
        high_norm = high_freq / nyquist
        
        # Ensure normalized frequencies are within valid range and properly ordered
        low_norm = max(low_norm, 0.001)
        high_norm = min(high_norm, 0.999)
        
        # Ensure high_norm is greater than low_norm
        if high_norm <= low_norm:
            high_norm = low_norm + 0.001
            if high_norm >= 0.999:
                # If we can't make high_norm greater than low_norm within valid range,
                # just return a simple passthrough
                return input_signal if filter_idx == 2 else np.zeros_like(input_signal)
        
        # Create bandpass filter
        b, a = signal.butter(self.filter_order, [low_norm, high_norm], btype='bandpass')
        
        # Apply filter
        filtered_signal = signal.filtfilt(b, a, input_signal)
        
        return filtered_signal
    
    def set_sample_rate(self, rate):
        """Set the sample rate"""
        self.sample_rate = rate 