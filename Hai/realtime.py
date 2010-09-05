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
SILENCE = -25.0
VOLUME_THRESHOLD = -15.0

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
midi_player.play(60 + Notes.C)
countdown(2)
print "Sing!"

# Open input stream, 16-bit mono at 44100 Hz
AUDIO_INPUT = p.open(
	format = pyaudio.paInt16,
	channels = 1,
	rate = 44100,
	input_device_index = 1,
	input = True)


	
chr = 0
time = 0
last_tone = None
last_played = None
last_played_time = 0
while True:
	# Read raw microphone data
	rawsamps = AUDIO_INPUT.read(CHUNK_SIZE)
	# Convert raw data to NumPy array
	samps = numpy.fromstring(rawsamps, dtype=numpy.int16)
	
	# get vol and pitch
	loudness = analyse.loudness(samps)
	pitch = Pitch(samps, mode = Modes.MINOR_PENTATONIC, key = Notes.C)
	
	# analyze pitch
	if loudness > VOLUME_THRESHOLD:
		tone = pitch.tone
		if tone != last_tone:
			last_time = time
			#
			# note changed
			#
			
			if last_played and tone and (abs(last_played - tone) > 11):
				# likely to be stray
				print "OVERLAP", (time - last_played_time)
				if (time - last_played_time) > 7:
					F_Stray = 0.8
				else:
				
					F_stray = 0.0	
			if last_played and tone and last_played == tone:
				print "REPEAT", (time - last_played_time)
				if (time - last_played_time) < 15:

					F_stray = 0.3
				else:
					F_stray = 1.0
			else:
				F_stray = 1.0
			

			D = F_stray
			print "%4s %3.f" % (pitch.to_tone_string() or "--", F_stray)
			
			
			if D > 0.6:
				midi_player.play(tone)
				if tone is not None:
					last_played = tone
					last_played_time = time
			
			last_tone = tone
	
	# advance time
	time += 1