import sys
from collections import deque
import itertools
import pygame
from camera_opencv import Webcam
from pygame.locals import *
from marker import Marker

class Concept():
	def __init__(self, pSize=(640, 480)):
		# Set up a pygame window display surface
		self.window = pygame.display.set_mode(pSize, 0)
		pygame.display.set_caption('Webcam Colour Tracking: ...Waiting for midi...')

		# Midi sender
		try:
			from src import SendMidi
			self.midiSender = SendMidi and SendMidi.SendMidi()
		except Exception, e:
			print "MIDI Failed: " + str(e)
			self.midiSender = None
		
		# Update title
		pygame.display.set_caption('Webcam Colour Tracking: ...Waiting for webcam...')

		# Set up clock for FPS counting
		self.clock = pygame.time.Clock()

		# Initialise camera
		self.webcam = Webcam(pSize)

		# Create a surface to capture to, same bit depth as window display surface
		self.webcamStill = pygame.surface.Surface(pSize, 0, self.window)
		self.output = pygame.surface.Surface(pSize, 0, self.window)

		# Settings
		self.debug = False
		self.stdOut = False
		self.minSize = 20
		self.filterQueueSize = 20
		self.midiOut = bool(self.midiSender)
		self.jumpLimit = 60
		self.thresholdWindowSize = 20
		
		try:
			pygame.font.init()
			self.debugFont = pygame.font.Font(None, 12)
		except:
			self.debugFont = None

		# Load identifiers
		self.markers = []
		# self.markers.append(["red", pygame.image.load ("red.png").convert_alpha(), (200, 50, 20), (80, 20, 15), (None, None)])
		# self.markers.append(["green", pygame.image.load ("green.png").convert_alpha(), (30, 150, 30), (20, 80, 20), (None, None)])
		# self.markers.append(["blue", pygame.image.load ("blue.png").convert_alpha(), (40, 40, 200), (20, 20, 80), (None, None)])
		# self.markers.append(["laser", pygame.image.load ("laser.png").convert_alpha(), (180, 200, 180), (70, 70, 70), (None, None)])

	def get_colour_location(self, pColour=(200, 50, 50), pColourThreshold=(80, 20, 20)):
		# Threshold against the colour we got before
		mask = pygame.mask.from_threshold(self.webcamStill, pColour, pColourThreshold)

		if self.debug:
			for m in mask.connected_components():
				if m.count() > self.minSize:
					pygame.draw.polygon(self.output, (255-pColour[0], 255-pColour[1], 255-pColour[2]), m.outline(10), 2)
					for r in m.get_bounding_rects():
						pygame.draw.rect(self.output, pColour, r, 1)

		# Keep only the largest blob of that colour
		connected = mask.connected_component()
		if connected.count() > self.minSize:
			return connected.centroid()
		return (None,None)

	def get_colour_match(self, pPosition):
		centrePixelColour = self.webcamStill.get_at(pPosition)
		
		windowMin = list(centrePixelColour)
		windowMax = list(centrePixelColour)

		
		for y in range(-self.thresholdWindowSize/2, self.thresholdWindowSize/2):
			for x in range(-self.thresholdWindowSize/2, self.thresholdWindowSize/2):
				# Should adjust if at edges to not go out of bounds
				pixelColour = self.webcamStill.get_at((pPosition[0]+x, pPosition[1]+y))
				for i in range(0, 3):
					if pixelColour[i] < windowMin[i]:
						windowMin[i] = pixelColour[i]
					if pixelColour[i] > windowMax[i]:
						windowMax[i] = pixelColour[i]

		threshold = (windowMax[0]-windowMin[0], windowMax[1]-windowMin[1], windowMax[2]-windowMin[2])

		return (centrePixelColour, threshold)

	def main(self, pFlipX=True, pFlipY=False):
		running = True

		while running:
			self.clock.tick()
			pygame.display.set_caption('Webcam Colour Tracking: %d fps' % self.clock.get_fps())
			
			# Check for events
			for e in pygame.event.get():
				if e.type == QUIT or (e.type == KEYDOWN and e.key == K_ESCAPE):
					# Exit cleanly
					self.webcam.stop()
					if self.midiSender:
						self.midiSender.close()
					running = False
				elif (e.type == KEYDOWN and e.key == K_d):
					self.debug = not self.debug
				elif (e.type == KEYDOWN and e.key == K_o):
					self.stdOut = not self.stdOut
				elif (e.type == KEYDOWN and e.key == K_f):
					pFlipX = not pFlipX
				elif (e.type == KEYDOWN and e.key == K_UP):
					self.minSize = self.minSize + 1
				elif (e.type == KEYDOWN and e.key == K_DOWN):
					self.minSize = self.minSize - 1
				elif (e.type == MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] == True):
					mousePos = pygame.mouse.get_pos()
					matchTuple = self.get_colour_match(mousePos)
					print matchTuple
					self.markers.append(Marker(str(len(self.markers)), pygame.image.load("misc.png").convert_alpha(), matchTuple[0], matchTuple[1], mousePos, self.filterQueueSize))
					#self.markers.append([str(len(self.markers)), pygame.image.load("misc.png").convert_alpha(), matchTuple[0], matchTuple[1], mousePos, deque(list(itertools.repeat((0, 0), self.filterQueueSize)))])

			self.webcam.read(self.webcamStill)
			if pFlipX or pFlipY:
				self.webcamStill = pygame.transform.flip(self.webcamStill, pFlipX, pFlipY)
			self.output = self.debug and self.webcamStill.copy() or self.webcamStill

			# Find marker positions
			for index, marker in enumerate(self.markers):
				tmp_coord = self.get_colour_location(pColour=marker.MatchColour, pColourThreshold=marker.MatchThreshold)
				if tmp_coord != (None,None):
					if marker.Position != (None,None):
						marker.SmoothingList.pop()
						marker.SmoothingList.appendleft(tmp_coord)
						filteredX = 0
						filteredY = 0
						for point in marker.SmoothingList:
							filteredX = filteredX + point[0]
							filteredY = filteredY + point[1]
						filtered = (filteredX/self.filterQueueSize, filteredY/self.filterQueueSize)
						delta = sum( [(x-y)**2 for (x,y) in zip(tmp_coord, filtered)])#marker.Position)])
						if delta < self.jumpLimit:
							marker.Position = filtered
							print "filter jump"
						else:
							marker.Position = tmp_coord

						if self.midiOut:
							for i in (0,1):
								val = (127.0 / float(self.window.get_size()[i])) * float(marker.Position[i])
								#self.midiSender.sendControlValue((index*2)+1+i, int(val))
								marker.MidiController.sendControlValue(int(val))
					else:
						marker.Position = tmp_coord
					self.output.blit(marker.Icon, (marker.Position[0]-8, marker.Position[1]-8))

			# Output markers (To screen and to stdout)
			if self.stdOut and len(self.markers) > 0:
				for index, marker in enumerate(self.markers):
					sys.stdout.write(marker.Name+'='+str(marker.Position[0])+','+str(marker.Position[1]))
					if index < len(self.markers)-1:
						sys.stdout.write(';')
				sys.stdout.write("\n")

			# Finally blit the output to the window
			if self.debug and self.debugFont:
				self.output.blit(self.debugFont.render("Min Match Size: %d" % self.minSize, 1, (10, 10, 10)), (0, 0))
				self.output.blit(self.debugFont.render("Filter Queue Size: %d" % self.filterQueueSize, 1, (10, 10, 10)), (0, 14))
				self.output.blit(self.debugFont.render("Min Jump Distance: %d" % self.jumpLimit, 1, (10, 10, 10)), (0, 28))
				self.output.blit(self.debugFont.render("Threshold Window Size: %d" % self.thresholdWindowSize, 1, (10, 10, 10)), (0, 42))
				self.output.blit(self.debugFont.render("MIDI output: %s" % "ON" if self.midiOut else "OFF", 1, (10, 10, 10)), (0, 56))
				self.output.blit(self.debugFont.render("Standard output: %s" % "ON" if self.stdOut else "OFF", 1, (10, 10, 10)), (0, 70))

			self.window.blit(self.output, (0, 0))
			pygame.display.flip()


# Run Proof of Concept
if __name__=='__main__':
	con = Concept()
	con.main()