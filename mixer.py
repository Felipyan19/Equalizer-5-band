import numpy as np

class SignalMixer:
    def __init__(self):
        # Default mixer states
        self.filter_gains = [1.0, 1.0, 1.0, 1.0, 1.0]
        
    def set_filter_gain(self, filter_idx, gain):
        """Set the gain for a specific filter output"""
        if 0 <= filter_idx < 5:
            self.filter_gains[filter_idx] = gain
            
    def get_filter_gain(self, filter_idx):
        """Get the gain for a specific filter output"""
        if 0 <= filter_idx < 5:
            return self.filter_gains[filter_idx]
        return 0.0
            
    def mix_signals(self, filtered_signals, filter_enabled):
        """Mix all the filtered signals according to enabled filters and gains"""
        if len(filtered_signals) != 5:
            raise ValueError("Expected 5 filtered signals")
            
        # Start with all zeros
        mixed_signal = np.zeros_like(filtered_signals[0])
        
        # Add each enabled filtered signal with its gain
        for i in range(5):
            if filter_enabled[i]:
                mixed_signal += filtered_signals[i] * self.filter_gains[i]
                
        return mixed_signal 