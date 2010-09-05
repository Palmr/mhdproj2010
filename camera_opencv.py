
import cv
from pygame import surfarray
import adaptors

class Webcam():
	def __init__(self):
		self.cp = cv.CaptureFromCAM(0)
	
	def get(self):
		numpyImage = adaptors.Ipl2NumPy(cv.QueryFrame(self.cp))
		return numpyImage.transpose(1,0,2)
	
	def read(self, surface):
		surfarray.blit_array(surface, self.get())
	
	def stop(self):
		cv.ReleaseCapture(self.cp)
