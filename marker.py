

from collections import deque
import itertools
from SendMidi import ControllerManager

class Marker():
	def __init__(self, pName, pIcon, pMatchColour, pMatchThreshold, pPosition, pFilterSize):
		self.Name = pName
		self.Icon = pIcon
		self.MatchColour = pMatchColour
		self.MatchThreshold = pMatchThreshold
		self.Position = pPosition
		self.SmoothingList = deque(list(itertools.repeat((0, 0), pFilterSize)))
		self.MidiController = ControllerManager().choose()