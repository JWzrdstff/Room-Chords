import numpy as np
import librosa
import os
import time
from scipy.fft import rfft, rfftfreq
from mido import Message
import mido

# --- Configuration ---
FOLDER_PATH = "/Users/jonathan/Projects/Room Chords/cricketsforFFT2" 
OUTPUT_PORT_NAME = None  # Will be set dynamically

BANDS = {
    "foundation": (60, 250),
    "mid_texture": (250, 4000),
    "upper_mid": (4000, 8000),
    "presence": (8000, 16000)
}

def hz_to_midi(hz):
    """Convert frequency to MIDI note number"""
    if hz <= 0: return 36
    return int(round(69 + 12 * np.log2(hz / 440)))

def find_available_output_port():
    """
    Dynamically detects the first available MIDI output on macOS.
    Returns True if a port is found, False otherwise.
    """
    try:
        # Get list of available output port names
        outputs = mido.get_output_names()
        
        if not outputs or len(outputs) == 0:
            print("Warning: No MIDI output ports detected by mido.")
            return False

        # Pick the first available valid port name
        for name in outputs:
            if isinstance(name, str) and len(name.strip()) > 0:
                OUTPUT_PORT_NAME = name.strip()
                print(f"✓ Auto-detected MIDI Output: '{OUTPUT_PORT_NAME}'")
                return True
        
        return False
        
    except Exception as e:
        print(f"Could not list MIDI ports: {e}")
        return False

def process_and_play():
    outport = None
    active_notes = [] # Track notes to ensure proper cleanup
    
    # --- Dynamic MIDI Initialization ---
    if find_available_output_port() is False:
        print("Error: Could not initialize MIDI port.")
        print("Hint: Make sure you have a MIDI driver installed and running (e.g., Loopback, CoreMIDI)")
        return

    try:
        outport = mido.open_output(OUTPUT_PORT_NAME)
        # We don't check .is_open() because that's not present in all mido versions
        print(f"✓ Connected to MIDI output: {OUTPUT_PORT_NAME}")
        
        # REMOVED: program_change test message. 
        # Sending this would alter the patch (A-1) or trigger state changes on many synths.
        # We rely strictly on Note events now.

    except Exception as e:
        print(f"Critical Error opening MIDI port '{OUTPUT_PORT_NAME}': {e}")
        return

    # Check for files
    if not os.path.exists(FOLDER_PATH):
        print(f"Error: Folder {FOLDER_PATH} does not exist.")
        outport.close()
        return

    files = [f for f in os.listdir(FOLDER_PATH) if f.endswith('.wav')]
    
    if not files:
        print("No .wav files found in the folder.")
        outport.close()
        return

    print(f"Processing {len(files)} recordings...")

    for file_name in files:
        path = os.path.join(FOLDER_PATH, file_name)
        
        try:
            # Load audio. sr=None preserves original sample rate
            y, sr = librosa.load(path, sr=None, mono=True)

            # FFT Analysis
            magnitudes = np.abs(rfft(y))
            frequencies = rfftfreq(len(y), 1/sr)

            midi_notes = []

            for band_name, (min_f, max_f) in BANDS.items():
                # Create a mask for the frequency range
                idx = np.where((frequencies >= min_f) & (frequencies <= max_f))[0]
                
                if len(idx) > 0:
                    # Find peak magnitude within that band
                    peak_idx_local = np.argmax(magnitudes[idx])
                    peak_freq = frequencies[idx[peak_idx_local]]
                    
                    note = hz_to_midi(peak_freq)
                    midi_notes.append(note)
                    print(f"  {file_name} | {band_name}: {peak_freq:.2f}Hz -> Note: {note}")

            # Unique notes for the chord (remove duplicates and sort)
            unique_notes = sorted(list(set(midi_notes)))

            # --- Execution ---
            if unique_notes:
                print(f"Playing Chord via {OUTPUT_PORT_NAME}: {unique_notes}")
                
                # Send all note_on messages simultaneously (or very quickly in sequence)
                for note in unique_notes:
                    # Ensure we are sending Note On, not triggering CCs or SysEx
                    outport.send(Message('note_on', note=note, velocity=127))
                    active_notes.append(note)
                
                # Small buffer to ensure all notes register before moving to next file
                time.sleep(0.1) 
            else:
                print("No significant frequencies detected in this file.")
            
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

        print("-" * 30)
        # Note: The script holds the chord until finished or stopped.
        # We will clean up notes explicitly at the end of each loop to prevent state drift,
        # though strictly speaking, many synths expect a global stop or note off sequence.
        
    # Cleanup - send note_off for all tracked notes before closing
    if active_notes:
        print("Cleaning up notes...")
        for note in active_notes:
            outport.send(Message('note_off', note=note, velocity=0))
    
    # Cleanup - close port
    outport.close()
    print("MIDI session closed.")

if __name__ == "__main__":
    process_and_play()
