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
		self.controlIdx = 0
		ControllerManager().controls["midi"] = self.createController
		
		# import musicify
		# self.musicify = musicify.Musicifier()
		# self.musicify.Run()
		
		print ControllerManager().controls
	
	def createController(self):
		self.controlIdx += 1
		return MidiController(self, self.controlIdx)
	
	def close(self):
		self.outputStream.close()
		self.musicify.Finish()
		pygame.midi.quit()

	def sendControlValue(self, pController, pValue):
		controlTuple = controlTuple = [[[176, pController, pValue, 0], pygame.midi.time()]]
		print "Sent: ",controlTuple
		self.outputStream.write(controlTuple)

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
	instance = []	
	def getinstance(*args, **kwargs):
		if not instance:
			instance.append( cls(*args, **kwargs) )
		return instance[0]
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
			ctrl = self.controls[raw_input("Choose controller: ")]
			return callable(ctrl) and ctrl() or ctrl
		except:
			print "Invalid controller"
			return None
