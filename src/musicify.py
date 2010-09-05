#!/usr/bin/env python

from pygame import pypm

import threading
import Queue
import time
import signal
import sys

class Musicifier:
   def __init__(self):
      self.device_in  = 0
      self.device_out = 0
      self.INPUT=0
      self.OUTPUT=1
      self.quitting = False
      self.queue = Queue.Queue()
      pypm.Initialize()

   def PrintDevices(self,InOrOut):
       for loop in range(pypm.CountDevices()):
           interf,name,inp,outp,opened = pypm.GetDeviceInfo(loop)
           if ((InOrOut == self.INPUT) & (inp == 1) |
               (InOrOut == self.OUTPUT) & (outp ==1)):
               print loop, name," ",
               if (inp == 1): print "(input) ",
               else: print "(output) ",
               if (opened == 1): print "(opened)"
               else: print "(unopened)"
       print


   def PickDevices(self):
      self.PrintDevices(self.INPUT)
      self.device_in = int(raw_input("Type input number: "))
      midi_in = pypm.Input(self.device_in);
      self.PrintDevices(self.OUTPUT)
      self.device_out = int(raw_input("Type output number: "))
      midi_out = pypm.Output(self.device_out);
      return (midi_in, midi_out)

   def AddMidiEvent(self, event):
      self.queue.put(event)

   def Run(self):
      (midi_in, midi_out) = self.PickDevices()
      self._RunInputThread(midi_in)
      self._RunOutputThread(midi_out)
      self.thread_input.join()
      print "Input thread quit"
      self.thread_output.join()
      print "Output thread quit"


   def Finish(self):
      print "Stopping portmidi"
      pypm.Terminate()
      print "Signalling threads to quit"
      self.quitting = True

   # PRIVATE METHODS

   def _InputCallback(self, midi_in,foo):
      while(not self.quitting):
         while not midi_in.Poll(): pass
         event = midi_in.Read(1)
         self.AddMidiEvent(event)


   def _CalcSecsPerTatum(self, tempo, tatums_per_beat ):
      return (60.0/tempo)/tatums_per_beat

   def _OutputCallback(self, midi_out,foo):

      tempo = 50.0
      beats_per_bar = 4
      tatums_per_beat = 4
      secs_per_tatum = self._CalcSecsPerTatum(tempo, tatums_per_beat)

      max_chord_roll = 0.1
      chord_roll_amount = 0.01

      notes = [] 

      tatum = 0
      beat = 0
      bar = 0
      base_note = 20

      resting = 0
      nitrous_oxide = False
      de_nitrous_oxide = False
      booster = 0
      choon_index = 0

      instrument = 3 # Piano 
      #instrument = 4 # Electric Piano 
      #instrument = 6 # Harpsichord

      midi_out.Write([[[0xC0,instrument,0],pypm.Time()]])

      def modal(mode, num):
         return mode[num % len(mode)] + 12*( num / len(mode))

      while(not self.quitting):
         print str(beat+1) + "." + str(tatum+1)
         time_to_sleep = secs_per_tatum
         empty = 0

         for note in notes:
            midi_out.Write([[[0x90,note,0],pypm.Time()]]);
         while (not empty):
            try:
               event = self.queue.get_nowait()
               print "Got message: time ",event[0][1],", ",
               print  event[0][0][0]," ",event[0][0][1]," ",event[0][0][2], event[0][0][3]

               control_code = event[0][0][0]
               target       = event[0][0][1]
               status_1     = event[0][0][2]
               
               controllers = dict( 
                     pitch = 2,
                     mode = 3,
                     tempo = 4,
                     chord_roll = 5,
                     rest = 46,
                     nitrous_oxide = 23,
                     de_nitrous_oxide = 33,
                     advance_choon = 41,
               )
               if ( target == controllers['pitch'] ):
                  base_note = (base_note+status_1/2)/2

               if ( target == controllers['mode'] ):
                  pass

               if ( target == controllers['tempo'] ):
                  tempo = status_1 + 30
                  secs_per_tatum = self._CalcSecsPerTatum(tempo, tatums_per_beat)

               if ( target == controllers['rest'] ):
                  resting = (status_1 == 127)
               
               if ( target == controllers['nitrous_oxide']):
                  nitrous_oxide = (status_1 == 127)

               if ( target == controllers['de_nitrous_oxide']):
                  de_nitrous_oxide = (status_1 == 127)

               if ( target == controllers['advance_choon']):
                  if (status_1 == 127):
                     choon_index += 1

               if ( target == controllers['chord_roll']):
                  chord_roll_amount = max_chord_roll * status_1/127.0

               self.queue.task_done()
            except Queue.Empty:
               empty = 1

         modes = dict(
            major = [0,2,4,5,7,9,11],
            minor = [0,2,3,5,7,8,11],
            minor_pent = [0,3,5,7,10],
            blues = [0,3,5,6,7,10],
            mixolydian = [0,2,4,5,7,9,10],
         )

         chords = dict(
            triad = [0,2,4],
            up = [0,1,2,3,4,5,6,7,8,9],
            big = [0,3,5, 9, 11, 13],
         )

         choon = [
            (0, 'minor_pent','triad'),
            (3, 'minor','triad'),
            (6, 'mixolydian','triad'),
         ]

         #choon_index = bar

         #if (tatum == 0):
         (key, mode_name,chord_type) = choon[choon_index%len(choon)]
         print mode_name
         mode = modes[mode_name]

         chord_choice = chords[chord_type]
         if (nitrous_oxide):
            cc1 = map (lambda x: x*2-5, chord_choice)
            booster += 2
            chord_in = cc1
         elif (de_nitrous_oxide):
            cc1 = map (lambda x: x*2-3, chord_choice)
            booster -= 2
            chord_in = cc1
         elif (tatum % tatums_per_beat == 0):
            chord_in = chord_choice
         else:
            chord_in = [chord_choice[(tatum%tatums_per_beat-1)%len(chord_choice)]]

         chord = map (lambda x: base_note+booster+x, chord_in)
         notes = map (lambda x: modal( mode , x+key), chord)

         if ( not resting ):
            i = 0
            for note in notes:
               midi_out.Write([[[0x90,note,100],pypm.Time()]]);
               time.sleep(chord_roll_amount)
               time_to_sleep -= chord_roll_amount
               if (time_to_sleep < 0.0): time_to_sleep = 0
               i += 1

         time.sleep(time_to_sleep)
         tatum+=1
         beat+=1
         if (beat % tatums_per_beat == 0): 
            beat = 0
         if (tatum % (tatums_per_beat*beats_per_bar) == 0):
            tatum = 0
            bar += 1

   def _RunInputThread(self, midi_in):
      self.thread_input = threading.Thread(target=self._InputCallback, name="input thread", args=(midi_in,1))
      self.thread_input.start()

   def _RunOutputThread(self, midi_out):
      self.thread_output = threading.Thread(target=self._OutputCallback, name="output thread", args=(midi_out,1))
      self.thread_output.start()





musicifier = Musicifier()
musicifier.Run()
