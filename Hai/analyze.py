import numpy
import pyaudio
import wave
import sys
import analyse
import matplotlib.pyplot as plt
import msvcrt
from boxbeat import Pitch, Modes, Notes


# constants
CHUNK_SIZE = 1024
DURATION_THRESHOLD = 10
RECORDING = False

# plot visualizations
def VIS_temp_note(time, pitch):
	plt.annotate(pitch.to_tone_string(), xy=(time,pitch), color="0.6")
def VIS_note(time, pitch):
	plt.annotate(pitch.to_tone_string(), xy=(time,pitch))
def VIS_loudness(loudness):
	plt.plot(loudness)
def VIS_pitch(pitch):
	plt.plot(pitch, "ro")


# output data format
class Data(object):
	def __init__(self):
		self.loudness = []
		self.pitch = []
		self.tones = []

DATA = Data()
	
# START	
p = pyaudio.PyAudio()
	
if len(sys.argv) < 2:
	RECORDING = True
	# Open input stream, 16-bit mono at 44100 Hz
	AUDIO_INPUT = p.open(
		format = pyaudio.paInt16,
		channels = 1,
		rate = 44100,
		input_device_index = 1,
		input = True)
else:
	wf = wave.open(sys.argv[1], 'rb')

	# open stream
	AUDIO_OUTPUT = p.open(format =
					pyaudio.paInt16,
					#p.get_format_from_width(wf.getsampwidth()),
					channels = wf.getnchannels(),
					rate = wf.getframerate(),
					output = True)
				
				# Initialize PyAudio


#
# STAGE 1
#
# Run analyse on input stream
#
if RECORDING:
	print "Sing!"
	chr = 0
	while chr == 0:
		# Read raw microphone data
		rawsamps = AUDIO_INPUT.read(CHUNK_SIZE)
		# Convert raw data to NumPy array
		samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
		# Show the volume and pitch
		
		DATA.loudness.append(analyse.loudness(samps))
		DATA.pitch.append(Pitch(samps, mode = Modes.MAJOR, key = Notes.G))
		# loop quit, only windows
		if msvcrt.kbhit():
			chr = msvcrt.getch()
	AUDIO_INPUT.close()

else:
	# read data
	data = wf.readframes(CHUNK_SIZE)
	while data != '':
		samps = numpy.fromstring(data, dtype=numpy.int16)
		pitch = Pitch(samps)
		loudness = analyse.loudness(samps)
		
		DATA.loudness.append(loudness)
		DATA.pitch.append(pitch)
		
		data = wf.readframes(CHUNK_SIZE)
	AUDIO_OUTPUT.close()
		
	


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
next_data = DATA.tones[0]
this_data = None
last_none_time = 0		# time of the last none
for i in range(1, len(DATA.tones)):
	# pick data
	this_data = next_data
	next_data = DATA.tones[i]
	
	# measure duration
	duration = next_data[0] - this_data[0] 
	
	KEEP = False
	# filter
	if next_data[1] == None or next_data[1].tone == None:
		if (this_data[0] - last_none_time) > DURATION_THRESHOLD:
			KEEP = True
		last_none_time = this_data[0]
	if duration > DURATION_THRESHOLD:
		KEEP = True
		
	# final decision
	if KEEP:
		VIS_note(*this_data)


plt.show()