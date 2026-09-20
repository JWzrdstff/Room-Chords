# Room-Chords

# .wav to automatic analysis, filtering, MIDI assignment, and external playback.

I wanted to to have a synthesizer play an arrangement of an environmental ambient recording programmatically.

I recorded a minute of backyard audio using a Zoom H2N stereo recorder with the mic capsule in a figure 8 pattern.
Prominent sounds were bugs and traffic from the freeway which is a quarter mile away. I dumped this audio into a folder.

My intent was to take this audio and use some kind of frequency analysis tool to figure out what the environmental
resonant peaks were in the recording so i could arrive at playable MIDI notes. To mitigate any errant transients (foot steps, dog barks) I wanted to
analyze the average highest peaking frequencies over the one minute duration of the recording. Below is a snapshot of the 
Logic Pro RTA showing prominent frequency response.

<img width="594" height="323" alt="RTA" src="https://github.com/user-attachments/assets/202a2ad3-dcf7-4d53-866f-e784d66f6add" />

I wanted to grab average peaks to avoid errant transients, but also wanted to do this over 4 different explicit bands of audio.
I separated the bands because I wanted low, mid, upper mid, and high frequencies to survive filtering as structural components of
the chord the MIDI notes will ultimately create. I also wanted to avoid a scenario where all the peaks were derived from one "timbre"
or limited range due to disproportionate SPL so the bands are separated as: 

Low 60hz-250hz
Mid 250hz-4000hz
Upper Mid 4000hz-8000hz
High 8000hz-16000hz

There are four bands because I was interested in creating four averaged notes per ambient recording. Multiple .wav files can be
analyzed from the same folder and four notes will be produced for each .wav creating a densely polyphonic performance.
The script uses rfft and rfftfreq to get data from the .wavs.

Once we have those average frequencies (one avg peak per band) script logic takes each of those frequencies and maps it
to the nearest MIDI note 0-127. Because The higher analyzed frequencies occur outside of the playable range, the script logic
drops those frequencies by an octave until they are within the playable MIDI range.

The script runs, executes the analysis, peak averaging per band, filtering, note assignment logic, and then looks for the first connected
MIDI device and sends MIDI control of USB from the computer, all from terminal.

# Libraries used:
librosa – For loading and handling the audio files.
mido – For communicating with your MIDI output ports and hardware.
numpy – For mathematical array operations and frequency calculations.
scipy – Specifically for the fast Fourier transform (scipy.fft) used in frequency analysis.

The script was written by Gemma 4 12B QAT and cleaned up by QWEN 3.5 9B, locally, on a Mac Mini M4 16GB base model.











