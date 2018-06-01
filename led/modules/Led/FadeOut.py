#!/usr/bin/env python

from __future__ import division
import RPi.GPIO as GPIO
import time
# import threading
# from multiprocessing import Process

class FadeOut:

	boardPinNumber = None
	name = None
	pwmPin = None
	pwmFreq = 100 # 1KHz
	currentTime = 0

	def __init__(self, boardPinNumber, name):
		print 'FadeOut.__init__()'
		self.boardPinNumber = boardPinNumber
		self.name = name
		self.setup()
	
	def setup(self):
		# Numbers GPIOs by physical location
		GPIO.setmode(GPIO.BOARD)
		# Set gpio pin mode as output (write)
		GPIO.setup(self.boardPinNumber, GPIO.OUT)
		# Set gpio pin low to off
		GPIO.output(self.boardPinNumber, GPIO.LOW)
		# set Frequece to 1KHz
		self.pwmPin = GPIO.PWM(self.boardPinNumber, self.pwmFreq)
		# start pwm with Duty Cycle at 0
		self.pwmPin.start(0)

	def blink(self, fadeDuration):
		self.blinkThread(fadeDuration)
		return;
		p = Process(target = self.blinkThread, args = (fadeDuration,))
		p.start()
		return
		thread = threading.Thread(
			group = None,
			target = self.blinkThread,
			name = None,
			args = (fadeDuration,),
			kwargs = {}
		)
		thread.daemon = True
		thread.start()
	
	def blinkThread(self, fadeDuration):
		dutyCycle = 100
		fadeStart = self.getTime()
		fadeEnd = fadeStart + fadeDuration
		fadeStepInterval = int(fadeDuration / 100)
		fadeStep = fadeStart
		print 'blink {name} fadeDuration {fadeDuration} fadeStepInterval {fadeStepInterval} fadeStart {fadeStart} fadeEnd {fadeEnd} fadeStep {fadeStep}'.format(
			name = self.name,
			fadeDuration = fadeDuration,
			fadeStepInterval = fadeStepInterval,
			fadeStart = fadeStart,
			fadeEnd = fadeEnd,
			fadeStep = fadeStep
		)
		# turn on led
		self.pwmPin.ChangeDutyCycle(dutyCycle)
		prevCurrentTime = 0
		while self.getTime() < fadeEnd:
			# don't do anything if time hasn't changed
			if self.currentTime == prevCurrentTime:
				continue
			# print 'currentTime {}'.format(self.currentTime)
			if fadeStep <= self.currentTime and dutyCycle >= 0:
				# print 'stepCount {} fadeStep {} dutyCycle {}'.format(stepCount, fadeStep, dutyCycle)
				self.pwmPin.ChangeDutyCycle(dutyCycle)
				# stepCount += 1
				dutyCycle -= 1
				fadeStep += fadeStepInterval
			prevCurrentTime = self.currentTime
		# print 'fadeEnd'
		# turn off led
		self.pwmPin.ChangeDutyCycle(0)
	
	def destroy(self):
		self.pwmPin.stop()
		GPIO.output(self.boardPinNumber, GPIO.LOW) # led off
		GPIO.cleanup() # Release resource
	
	def getTime(self):
		self.currentTime = int(round(time.time() * 1000))
		return self.currentTime