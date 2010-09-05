import analyse

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")

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

class Pitch(float):
	"""
		Pitch class stores the raw pitch as detected from
		a sample. Contains functions to convert to a tone.
		
		Note that 0.0 is used as No note, so do not sing the
		lowest C.
	"""
	__slots__ = ('_tone', '_octave', '_note')
	
	def __new__(self, sample):
		if isinstance(sample, float):
			value = sample
		else:
			# assume it's something to be analysed
			value = analyse.musical_detect_pitch(sample) or 0.0
		return float.__new__(self, value)
	
	def __init__(self, sample):
		self._tone = None
		self._octave = None
		self._note = None
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
		return self.tone and self.tone % 12
			
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