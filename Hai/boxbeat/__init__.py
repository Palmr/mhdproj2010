import analyse

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

class Notes:
	C = 0
	CSHARP = 1
	D = 2
	DSHARP = 3
	E = 4
	F = 5
	FSHARP = 6
	G = 7
	GSHARP = 8
	A = 9
	ASHARP = 10
	B = 11
	
def lazy_property(name):
	def proc(f):
		def wrapped(self):
			value = getattr(self, name) 
			if not value:
				value = f(self)
				setattr(self, name, value)
			return value
		return property(wrapped)
	return proc

def snap_note(value, values):
	""" 0 and 12 must always be included at ends """
	for i in range(len(values) - 1):
		u = values[i + 1] 
		if u > value:
			l = values[i]
			w = u - l
			return l + w * int(round((value - l) / float(w), 0))

class Modes:
	ALL_NOTES = range(13)
	MAJOR = [0,2,4,5,7,9,11,12]
	HARMONIC_MINOR = [0,2,3,5,7,8,11,12]
	MELODIC_MINOR = [0,2,3,5,7,9,11,12]
	ACTION = [0,3,5,7,10,12]
	JAZZ = [0,3,4,5,6,7,10,11,12]
	
	
	
class Pitch(float):
	"""
		Pitch class stores the raw pitch as detected from
		a sample. Contains functions to convert to a tone.
		
		Note that 0.0 is used as No note, so do not sing the
		lowest C.
	"""
	__slots__ = ('_tone', '_octave', '_note', '_mode', '_key')
	
	def __new__(self, sample, mode = Modes.ALL_NOTES, key = Notes.C):
		if isinstance(sample, float):
			value = sample
		else:
			# assume it's something to be analysed
			value = analyse.musical_detect_pitch(sample) or 0.0
		return float.__new__(self, value)
	
	def __init__(self, sample, mode = Modes.ALL_NOTES, key = Notes.C):
		self._tone = None
		self._octave = None
		self._note = None
		self._mode = mode
		self._key = key
		pass
		
	@lazy_property("_tone")
	def tone(self):	
		value = int(round(self, 0))
		return (value if value > 0 else None)
			
			
	@lazy_property("_octave")
	def octave(self):
		return self.tone and self.tone / 12
			
	@lazy_property("_note")
	def note(self):
		return self.tone and (snap_note((self.tone - self._key) % 12, self._mode) + self._key) % 12
			
	def to_tone_string(self):
		if self.tone:
			return "%s%s" % (self.octave, NOTE_NAMES[self.note])
		else:
			return ""
			
	@staticmethod
	def from_tone_to_string(tone):
		if tone:
			return "%s%s" % (tone / 12, NOTE_NAMES[tone % 12])
		else:
			return ""