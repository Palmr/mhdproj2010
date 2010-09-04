import pygame.midi

class SendMidi():
	def __init__(self):
		pygame.midi.init()
		self.outputStream = pygame.midi.Output(pygame.midi.get_count()-1)

	def close(self):
		self.outputStream.close()
		pygame.midi.quit()

	def sendControlValue(self, pController, pValue):
		controlTuple = [[[176, pController, pValue, 0], pygame.midi.time()]]
		self.outputStream.write(controlTuple)
		print "Sent: ",controlTuple

	def sendNote(self, pNote, pVelocity=100, pChannel=0):
		self.outputStream.note_on(pNote, pVelocity, pChannel)