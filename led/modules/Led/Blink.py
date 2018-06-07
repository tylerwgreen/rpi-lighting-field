#!/usr/bin/env python

import RPi.GPIO as GPIO
import time

class Blink:

	boardPinNumber = None

	def __init__(self, boardPinNumber):
		print 'blink.construct()'
		self.boardPinNumber = boardPinNumber
	
	def setup(self):
		GPIO.setmode(GPIO.BOARD)						# Numbers GPIOs by physical location
		GPIO.setup(self.boardPinNumber, GPIO.OUT)		# Set boardPinNumber's mode is output
		GPIO.output(self.boardPinNumber, GPIO.LOW)		# Set boardPinNumber low to off led
		print 'using pin%d'%self.boardPinNumber

	def loop(self):
		while True:
			GPIO.output(self.boardPinNumber, GPIO.HIGH)	# led on
			print '...led on'
			time.sleep(1)	
			GPIO.output(self.boardPinNumber, GPIO.LOW)	# led off
			print 'led off...'
			time.sleep(1)

	def destroy(self):
		GPIO.output(self.boardPinNumber, GPIO.LOW)		# led off
		GPIO.cleanup()									# Release resource