
import cv

class Webcam():
	def __init__(self):
		self.cp = cv.CaptureFromCAM(0)
	
	def get(self):
		return cv.QueryFrame(self.cp)

cv.NamedWindow("res", cv.CV_WINDOW_AUTOSIZE)
cv.ShowImage("res", Webcam().get())

while True:
	pass
	