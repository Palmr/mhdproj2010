#!/usr/bin/env python

import pypm


pypm.Initialize()

latency = 0
device = 2

midiOut = pypm.Output(device, latency)

pipe = open('/tmp/vimmidi.pipe','r')

while (pipe.readline()):
   1

def noteOn(note):
   midiOut.Write([[[0x90,note,100],pypm.Time()]])
def noteOff(note):
   midiOut.Write([[[0x90,note,0],pypm.Time()]])

def chromatic(row, col):
   return row+col

def modal(mode, num):
   return mode[num % len(mode)] + 12*( num / len(mode))

def modRange(min, max, note):
   return min+(note % (max-min))

def chooseNote(row, col):
   #return modRange(27,108,chromatic(0, col))
   return modRange(30, 128, modal([0,2,3,5,7,8,11],col-1))

prevnote = -1

while (1):
   line = pipe.readline()
   line.rstrip("\n")
   if (line):
      print line
      fields = line.split()
      row = int(fields[1])
      col = int(fields[2])
      note = chooseNote(row, col)
      if (prevnote > -1):
         noteOff(prevnote)
      prevnote = note
      noteOn(note)


del midiOut
