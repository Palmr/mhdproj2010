import numpy
import pyaudio
import wave
import sys
import analyse
import matplotlib.pyplot as plt
from boxbeat import Pitch


# constants
CHUNK_SIZE = 1024
DURATION_THRESHOLD = 10

# plot visualizations
def VIS_temp_note(time, pitch):
	plt.annotate(pitch.to_tone_string(), xy=(time,pitch), color="0.6")
def VIS_note(time, pitch):
	plt.annotate(pitch.to_tone_string(), xy=(time,pitch))
def VIS_loudness(loudness):
	plt.plot(loudness)
def VIS_pitch(pitch):
	plt.plot(pitch, "ro")
	
	
if len(sys.argv) < 2:
	print "Plays a wave file.\n\n" +\
		"Usage: %s filename.wav" % sys.argv[0]
	sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')

p = pyaudio.PyAudio()

# open stream
stream = p.open(format =
				pyaudio.paInt16,
				#p.get_format_from_width(wf.getsampwidth()),
				channels = wf.getnchannels(),
				rate = wf.getframerate(),
				output = True)

# read data
data = wf.readframes(CHUNK_SIZE)

# output data
class Data(object):
	def __init__(self):
		self.loudness = []
		self.pitch = []
		self.tones = []

DATA = Data()

#
# STAGE 1
#
# Run analyse on input stream
#
while data != '':
	samps = numpy.fromstring(data, dtype=numpy.int16)
	pitch = Pitch(samps)
	loudness = analyse.loudness(samps)
	
	DATA.loudness.append(loudness)
	DATA.pitch.append(pitch)
	
	data = wf.readframes(CHUNK_SIZE)
	
	

stream.close()
p.terminate()

VIS_loudness(DATA.loudness)
VIS_pitch(DATA.pitch)


#
# STAGE TWO
#
# analyze pitches and pick out sustains and their
# durations
# TOOD pick volume up
last_tone = None
for time, pitch in enumerate(DATA.pitch):
	tone = pitch.tone
	if tone != last_tone:
		# change of tone. Record new note and time
		DATA.tones.append((time, pitch))	
		last_tone = tone
		
		# plot it
		VIS_temp_note(time, pitch)


		
#
# STAGE THREE
# 
# Filtering
#

# final note
DATA.tones.append((len(DATA.pitch), None))
next_note = DATA.tones[0]
this_note = None
for i in range(1, len(DATA.tones)):
	# pick data
	this_note = next_note
	next_note = DATA.tones[i]
	
	# measure duration
	duration = next_note[0] - this_note[0] 
	
	# filter
	if duration > DURATION_THRESHOLD:
		VIS_note(*this_note)




plt.show()