import pygame.midi
import time

MAGIC = 0

class SendMidi():
	def __init__(self):
		pygame.midi.init()
		self.outputStream = pygame.midi.Output(MAGIC)

	def close(self):
		self.outputStream.close()
		pygame.midi.quit()

	def sendControlValue(self, pController, pValue):
		controlTuple = [[[176, pController, pValue, 0], pygame.midi.time()]]
		self.outputStream.write(controlTuple)

	def sendNote(self, pNote, pVelocity=100, pChannel=0):
		self.outputStream.note_on(pNote, pVelocity, pChannel)
		
midiControl = SendMidi()
midiControl.outputStream.set_instrument(115, channel = 0)
midiControl.sendNote(60, 20)
time.sleep(1)

midiControl.close()