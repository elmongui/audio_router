import os
import sys
import tkinter as tk
from tkinter import ttk  # Import ttk for the separator
import sounddevice as sd
import soundfile as sf
from pydub import AudioSegment
from pydub.playback import play

# Function to get the path to the data file whether running from .exe or normally
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller stores the path in _MEIPASS when running the .exe
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Load the audio files
da_file = resource_path('da.wav')
ba_file = resource_path('ba.wav')

# Function to load the audio file (you can use pydub to handle MP3s)
def load_audio(file):
    ## Open the file and get details
    with sf.SoundFile(file) as f:
    #    print(f"Reading {file} --> "
    #        f"Sample Rate: {f.samplerate} Hz, "
    #        f"Channels: {f.channels}, "
    #        #f"Format: {f.format}, "
    #        #f"Subtype: {f.subtype}, "
    #        f"Frames: {f.frames}, "
    #        f"Duration: {f.frames / f.samplerate:.2f} sec")
        assert f.channels == 1, "Input file is not mono"

    audio = AudioSegment.from_wav(file)
    return audio

da_audio = load_audio(da_file)
ba_audio = load_audio(ba_file)

# Speaker mapping for stereo (left and right channels)
speaker_mapping = {
    0: [1],  # Left channel
    1: [2],  # Right channel
}

# Function to play audio on specific channels
def play_audio(audio_file, speaker_channel, device_id):
    data, fs = sf.read(audio_file)
    # Play the audio on the specified channel (left or right)
    sd.play(data, fs, device=device_id, mapping=speaker_channel)
    sd.wait()

# Function to play files based on switch states
def play_audio_files():
    device_id = int(device_combobox.get().split(':')[0])  # Get selected device ID
    for i in range(2):  # Only 2 speakers (left and right)
        if switches[i].get() == "da": # Check the value of the Radiobutton
            play_audio(da_file, speaker_mapping[i], device_id)  # Play da.mp3 if switch is on
        else:
            play_audio(ba_file, speaker_mapping[i], device_id)  # Play ba.mp3 if switch is off

# Get available output devices
def get_output_devices():
    devices = sd.query_devices()
    output_devices = []
    for idx, device in enumerate(devices):
        if device['max_output_channels'] > 0:
            output_devices.append(f"{idx}: {device['name']}")
    return output_devices
    
# Create the main window
root = tk.Tk()
root.title("Audio Router")

# Make the window non-resizable
root.resizable(False, False)

# Create a combobox to select the output device
output_devices = get_output_devices()
device_combobox = ttk.Combobox(root, values=output_devices, state="readonly", width=50, font=("Helvetica", 10, "bold"))
device_combobox.set("Select Output Device ...")  # Default text
device_combobox.pack(pady=10)

# Create a frame to hold both switches side by side
switch_frame = tk.Frame(root)
switch_frame.pack(pady=10)

# Variables to store the selected value for each speaker
switches = []
for speaker in ['Left', 'Right']:
    frame = tk.Frame(switch_frame)
    frame.pack(side=tk.LEFT, padx=60)

    # Add label for each speaker
    speaker_label = tk.Label(frame, text=speaker, font=("Helvetica", 12, "bold"))
    speaker_label.pack(side=tk.TOP)

    # Variable to hold the current selection
    var = tk.StringVar(value="da")

    # Add radiobuttons for 'ba' and 'da'
    rb1 = tk.Radiobutton(frame, text="ba", variable=var, value="ba", font=("Helvetica", 12))
    rb1.pack(side=tk.TOP)
    
    rb2 = tk.Radiobutton(frame, text="da", variable=var, value="da", font=("Helvetica", 12))
    rb2.pack(side=tk.TOP)
    
    switches.append(var)

# Add a horizontal separator (ruler) after each switch section
separator = ttk.Separator(root, orient='horizontal')
separator.pack(fill='x', pady=0)  # Add padding for better spacing

# Frame to hold both Play and Quit buttons side by side
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

# Play button (initially disabled)
play_button = tk.Button(button_frame, text="Play", command=play_audio_files, state=tk.DISABLED)
play_button.pack(side=tk.LEFT, padx=10)

# Quit button to close the application
quit_button = tk.Button(button_frame, text="Quit", command=root.quit)
quit_button.pack(side=tk.LEFT, padx=10)

# Function to enable the play button when a device is selected
def enable_play_button(event):
    if device_combobox.get() != "Select Output Device":
        play_button.config(state=tk.NORMAL)

# Bind the combobox selection event to enable the Play button
device_combobox.bind("<<ComboboxSelected>>", enable_play_button)

# Start the GUI loop
root.mainloop()
