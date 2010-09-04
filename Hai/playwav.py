import numpy
import pyaudio
import wave
import sys
import analyse
import matplotlib.pyplot as plt

chunk = 1024

if len(sys.argv) < 2:
	print "Plays a wave file.\n\n" +\
		"Usage: %s filename.wav" % sys.argv[0]
	sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = pyaudio.PyAudio()

# open stream
stream = p.open(format =
				p.get_format_from_width(wf.getsampwidth()),
				channels = wf.getnchannels(),
				rate = wf.getframerate(),
				output = True)

# read data
data = wf.readframes(chunk)


vols = []
pitches = []
# play stream
while data != '':
	samps = numpy.fromstring(data, dtype=numpy.int16)
	pitch = analyse.musical_detect_pitch(samps)
	loudness = analyse.loudness(samps)
	
	vols.append(loudness)
	pitches.append(pitch)
	
	print "%3.1f %3.1f" % (loudness, pitch or 0.0)
	
	# output
	stream.write(data)
	data = wf.readframes(chunk)
	
	

stream.close()
p.terminate()

plt.plot(vols)
plt.plot(pitches, "ro")
plt.show()