import numpy
import pyaudio
import analyse
import matplotlib.pyplot as plt

# Initialize PyAudio
pyaud = pyaudio.PyAudio()

# Open input stream, 16-bit mono at 44100 Hz
stream = pyaud.open(
	format = pyaudio.paInt16,
	channels = 1,
	rate = 44100,
	input_device_index = 1,
	input = True)

    
vols = []
pitches  = []
i = 0
while i < 100:
	# Read raw microphone data
	rawsamps = stream.read(1024)
	# Convert raw data to NumPy array
	samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
	# Show the volume and pitch
	
	vols.append(analyse.loudness(samps))
	pitches.append(analyse.musical_detect_pitch(samps) or 0.0)
	
	print vols[-1]
	
	i += 1
	
plt.plot(vols)
plt.plot(pitches, "ro")
plt.show()