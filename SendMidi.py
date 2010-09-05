import pygame.midi

pygame.midi.init()
if not pygame.midi.get_count():
	raise ImportError("Sorry, no MIDI devices found")

INPUT=0
OUTPUT=1

class SendMidi():
	def __init__(self, device=0):
		if not device:
			if pygame.midi.get_count() > 2:
				printDevices(OUTPUT)
				device = int(raw_input("Type output number: "))
			else:
				device = 1
		
		self.outputStream = pygame.midi.Output(device)

	def close(self):
		self.outputStream.close()
		pygame.midi.quit()

	def sendControlValue(self, pController, pValue):
		controlTuple = (((176, pController, pValue, 0), pygame.midi.time()))
		self.outputStream.write(controlTuple)
		print "Sent: ",controlTuple

	def sendNote(self, pNote, pVelocity=100, pChannel=0):
		self.outputStream.note_on(pNote, pVelocity, pChannel)

def printDevices(inOrOut):
	for loop in range(pygame.midi.get_count()):
		interf,name,inp,outp,opened = pygame.midi.get_device_info(loop)
		if ((inOrOut == INPUT) & (inp == 1) |
			(inOrOut == OUTPUT) & (outp ==1)):
			print loop, name," ",
			if (inp == 1): print "(input) ",
			else: print "(output) ",
			if (opened == 1): print "(opened)"
			else: print "(unopened)"
	print


def singleton(cls):
	instance = 0	
	def getinstance(*args, **kwargs):
		if not instance:
			instance = cls(*args, **kwargs)
		return instance
	return getinstance


class MidiController:
	def __init__(self, port, controller):
		self.port = port
		self.controller = controller
	
	def sendControlValue(self, value):
		self.port.sendControlValue(self.controller, value)
		
		
@singleton    
class ControllerManager:
	def __init__(self):
		self.controls = {}
	
	def choose(self):
		i = 0
		for k,v in self.controls.iteritems():
			print k
			
		try:
			return self.controls[raw_input("Choose controller: ")]
		except:
			print "Invalid controller"
			return None

