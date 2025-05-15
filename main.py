import tkinter as tk
import numpy as np
import matplotlib
import traceback
import sys

matplotlib.use('TkAgg')  

from signal_generator import SignalGenerator
from filters import EqualizerFilter
from mixer import SignalMixer
from ui import EqualizerUI

def main():
    try:
        signal_gen = SignalGenerator()
        equalizer = EqualizerFilter()
        mixer = SignalMixer()
        
        root = tk.Tk()
        app = EqualizerUI(root, signal_gen, equalizer, mixer)
        
        app.run()
    except Exception as e:
        error_msg = f"Error: {str(e)}\n\n{traceback.format_exc()}"
        print(error_msg)
        
        try:
            root = tk.Tk()
            root.title("Error")
            root.geometry("800x400")
            
            label = tk.Label(root, text="An error occurred:", font=("Arial", 12, "bold"))
            label.pack(pady=(20, 10))
            
            error_text = tk.Text(root, wrap=tk.WORD, bg='#f0f0f0', height=15)
            error_text.insert(tk.END, error_msg)
            error_text.config(state=tk.DISABLED)
            error_text.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
            
            close_button = tk.Button(root, text="Close", command=root.destroy)
            close_button.pack(pady=20)
            
            root.mainloop()
        except:
            pass

if __name__ == "__main__":
    main() 