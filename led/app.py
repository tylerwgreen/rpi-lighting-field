#!/usr/bin/env python

from __future__ import division
import time
from modules.Led.FadeOut import FadeOut
import threading
# from multiprocessing import Process

class App:
	
	blinkInterval = 2000 # milliseconds
	blinkTime = None
	fadeDuration = 1000 # milliseconds
	currentTime = None
	
	def __init__(self):
		print 'App.__init__()'
		if self.blinkInterval < self.fadeDuration:
			raise Exception('blinkInterval {blinkInterval} is less than fadeDuration {fadeDuration}'.format(blinkInterval = self.blinkInterval, fadeDuration = self.fadeDuration))
		self.fadingLedBlue = FadeOut(11, 'Blue')
		# self.fadingLedRed = FadeOut(13, 'Red')
		# self.fadingLedGreen = FadeOut(15, 'Green')
		# self.fadingLedYellow = FadeOut(16, 'Yellow')
		try:
			self.setBlinkTime()
			self.blinkLeds()
			prevCurrentTime = 0
			while True:
				# don't do anything if time hasn't changed
				if self.currentTime == prevCurrentTime:
					# print 'continue'
					self.getTime()
					continue
				if self.currentTime >= self.blinkTime:
					print 'blink'
					self.setBlinkTime()
					self.blinkLeds()
				# print 'set prevCurrentTime {}'.format(self.currentTime)
				prevCurrentTime = self.currentTime
		except KeyboardInterrupt:
			self.destroyLeds()
	
	def setBlinkTime(self):
		self.blinkTime = self.getTime() + self.blinkInterval
	
	def blinkLeds(self):
		print 'App.blinkLeds()'
		thread = threading.Thread(
			group = None,
			target = self.fadingLedBlue.blink,
			name = None,
			args = (self.fadeDuration,),
			kwargs = {}
		)
		thread.daemon = True
		thread.start()
		# self.fadingLedRed.blink(self.fadeDuration)
		# self.fadingLedGreen.blink(self.fadeDuration)
		# self.fadingLedYellow.blink(self.fadeDuration)
	
	def destroyLeds(self):
		print 'App.destroyLeds()'
		self.fadingLedBlue.destroy()
		# self.fadingLedRed.destroy()
		# self.fadingLedGreen.destroy()
		# self.fadingLedYellow.destroy()
	
	def getTime(self):
		self.currentTime = int(round(time.time() * 1000))
		# print 'App.getTime() {}'.format(self.currentTime)
		return self.currentTime

if __name__ == '__main__':
	appObject = App()