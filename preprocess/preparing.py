import librosa, librosa.display
import matplotlib.pyplot as plt
import numpy as np

# audio files load
file = "blues.00000.wav"

# waveform


signal, sr = librosa.load(file, sr=22050) # sr * T -> 22050 * 30

# librosa.display.waveplot(signal, sr=sr)
# plt.xlabel("Time")
# plt.ylabel("Amplitude")
# plt.show()


# fft -> spectrum
fft = np.fft.fft(signal)

magnitude = np.abs(fft)
frequency = np.linspace(0, sr, len(magnitude))
left_frequency = frequency[:int(len(frequency) / 2)]
left_magnitude = magnitude[:int(len(frequency)/ 2)]

# plt.plot(left_frequency, left_magnitude)
# plt.xlabel("Frequency")
# plt.ylabel("Magnitude")
# plt.show()

# stft -> spectogram

n_fft = 2048
hop_length = 512

stft = librosa.core.stft(signal, hop_length=hop_length, n_fft=n_fft)
spectogram = np.abs(stft)

log_spectogram = librosa.amplitude_to_db(spectogram)

librosa.display.specshow(spectogram, sr=sr, hop_length=hop_length)

#plt.xlabel("Time")
#plt.ylabel("Frequency")
#plt.colorbar()
#plt.show()

# MFCCs 

MFCC = librosa.feature.mfcc(signal, n_fft=n_fft, hop_length=hop_length, n_mfcc =13)
librosa.display.specshow(MFCC, sr=sr, hop_length=hop_length)
plt.xlabel("Time")
plt.ylabel("MFCC")
plt.colorbar()
plt.show()
