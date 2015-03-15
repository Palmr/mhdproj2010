# Music Hack Day project #
## Requirements ##
  * Python 2.6
  * OpenCV
  * NumPy
  * Webcam
  * Midi port (LoopBe)

## About the hack ##
Inspired by boredom, lack of money for fancy MIDI controllers and colourful fruit. This hack empowers people without fancy MIDI controllers to embrace their creativity in a new way.

The hack is a python script that lets a webcam track the position of various coloured objects at the same time, and use those positions as MIDI output.
Objects can be interpreted as buttons (on if it's in view, off if not), horizontal and vertical sliders, or like an XY trackpad.
This can be hooked up to any MIDI controllable application, like Ableton, to control anything a normal MIDI controller could. Or, as demonstrated, with python scripts containing custom MIDI controller functions on them to alter params.

### Coded by ###
  * Sean Micklethwaite
  * Dan Horgan
  * Mac Duy, Hai
  * Nick Palmer