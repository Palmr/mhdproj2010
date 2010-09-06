

from collections import deque
import itertools
from src.SendMidi import ControllerManager

class Marker():
	def __init__(self, pName, pIcon, pMatchColour, pMatchThreshold, pPosition, pFilterSize):
		self.Name = pName
		self.Icon = pIcon
		self.MatchColour = pMatchColour
		self.MatchThreshold = pMatchThreshold
		self.Position = pPosition
		self.SmoothingList = deque(list(itertools.repeat((0, 0), pFilterSize)))
		self.ControllerType = raw_input("Choose controller type [X, Y, XY, Button]: ").upper()
		
		if self.ControllerType == "XY":
			self.MidiController = (ControllerManager().choose(), ControllerManager().choose())
		else:
			self.MidiController = ControllerManager().choose()
		
		self.OnScreen = True
	
	def send(self, window, xlock, ylock):
		x = (127.0 / float(window.get_size()[0])) * float(self.Position[0])
		y = (127.0 / float(window.get_size()[1])) * float(self.Position[1])
		
		if self.ControllerType == "XY":
			if not ylock:
				self.MidiController[0].sendControlValue(int(x))
			if not xlock:
				self.MidiController[1].sendControlValue(int(y))
		elif self.ControllerType == "X":
				self.MidiController.sendControlValue(int(x))
		elif self.ControllerType == "Y":
				self.MidiController.sendControlValue(int(y))
		elif self.ControllerType.startswith("B"):
				if not self.OnScreen:
					self.MidiController.sendControlValue(127)
					self.OnScreen = True

	def offscreen(self):
		if self.ControllerType == "B" and self.OnScreen:
			self.MidiController.sendControlValue(0)
			self.OnScreen = False