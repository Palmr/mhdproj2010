import numpy
import pyaudio
import wave
import sys
import analyse
import matplotlib.pyplot as plt
import msvcrt
from boxbeat import Pitch, Modes, Notes, MidiControl, snap_to_values
from time import sleep


midi_player = MidiControl()

# constants
CHUNK_SIZE = 1024
DURATION_THRESHOLD = 10
RECORDING = False
TIMESTEP = 44100.0 / CHUNK_SIZE
LAG = 10

# plot visualizations
def VIS_temp_note(time, pitch):
	plt.annotate(pitch.to_tone_string(), xy=(time,pitch), color="0.6")
def VIS_note(time, pitch):
	plt.annotate(pitch.to_tone_string(), xy=(time,pitch))
def VIS_loudness(loudness):
	plt.plot(loudness)
def VIS_pitch(pitch):
	plt.plot(pitch, "ro")
def VIS_beat(interval, max):
	for x in range(0, max, interval):
		plt.vlines(x + LAG, -20, 60)

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


def countdown(secs):
	while secs > 0:
		print secs
		sleep(1)
		secs -= 1
				
#
# STAGE 1
#
# Run analyse on input stream
#
if RECORDING:
	midi_player.play(60 + Notes.C)
	countdown(3)
	print "Sing!"
	
	# Open input stream, 16-bit mono at 44100 Hz
	AUDIO_INPUT = p.open(
		format = pyaudio.paInt16,
		channels = 1,
		rate = 44100,
		input_device_index = 1,
		input = True)
	
	chr = 0
	i = 0
	while chr == 0:
		# Read raw microphone data
		rawsamps = AUDIO_INPUT.read(CHUNK_SIZE)
		# Convert raw data to NumPy array
		samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
		# Show the volume and pitch
		
		DATA.loudness.append(analyse.loudness(samps))
		DATA.pitch.append(Pitch(samps, mode = Modes.MINOR_PENTATONIC, key = Notes.C))
		# loop quit, only windows
		if msvcrt.kbhit():
			chr = msvcrt.getch()
		if  i <= 0:
			midi_player.set_instrument(115, channel = 1) # clicky instrument
			midi_player.play(60, 20, channel = 1)
			i = 35
		i -= 1
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
VIS_beat(35, len(DATA.pitch))

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
	
	# snap duration
	duration = snap_to_values(duration, [0, 35 / 2.0, 35, 35 + 35 / 2.0, 70, 105, 140])
	# final decision
	if KEEP:	
		VIS_note(*this_data)
		# play the note if avail
		if this_data[1] != None and this_data[1].tone != None:
			midi_player.play(this_data[1].tone)	
	sleep(duration / TIMESTEP)


		

plt.show()