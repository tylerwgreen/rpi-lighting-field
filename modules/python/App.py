#!/usr/bin/env python
# encoding: utf-8

import os
import logging
import sys
# sys.path.append('/mnt/dietpi_userdata/projects/rpi-lighting-field/modules/python')

from NodeInterface import NodeInterface
from AudioAnalyzer import AudioAnalyzer

class App:

	nodeInterface = None
	audioAnalyzer = None

	# @profile
	def __init__(self):
		# configure dirs
		
		appDir = os.path.dirname(os.path.realpath(__file__)) + '/../..'
		logDir = appDir + '/var/log/python'
		# configure logger
		logging.basicConfig(
			filename = logDir + '/app.log',
			level = logging.DEBUG
		)
		self.logger = logging.getLogger(__name__)
		
		# configure dependencies
		self.nodeInterface = NodeInterface()
		self.registerNodeInterfaceCommands()
		# configure audioAnalyzer and suppress warning/errors
		self.audioAnalyzer = AudioAnalyzer(self.nodeInterface)
		# App is configured, start the main loop
		self.nodeInterface.message('App.__init__ success')
		# self.play({'file': 'assets/audio/440-octaves.wav'})
		# self.play({'file': 'assets/audio/1k-octaves.wav'})
		# self.play({'file': 'assets/audio/cello.wav'})
		# self.play({'file': 'assets/audio/drums-01.wav'})
		# self.play({'file': 'assets/audio/technologic-real.wav'})
		# self.play({'file': 'assets/audio/getaway-16-44.wav'})
		# self.play({'file': 'assets/audio/audiocheck.net_pinknoise.wav'})
		# self.play({'file': 'assets/audio/audiocheck.net_whitenoisegaussian.wav'})
		self.mainLoop()
	
	def mainLoop(self):
		while True:
			self.nodeInterface.listen()
	
	def registerNodeInterfaceCommands(self):
		# these are commands that can be called from node
		self.nodeInterface.registerCommand('play', self.play)
		self.nodeInterface.registerCommand('stop', self.stop)
	
	# @profile
	def play(self, data):
		self.audioAnalyzer.play(data['file'])
		self.nodeInterface.message('App.play success')

	def stop(self):
		self.audioAnalyzer.stop()
		self.nodeInterface.message('App.stop success')

if __name__ == '__main__':
	app = App()

'''
{"data":{"type":"command","id":"play","attributes":{"file":"assets/audio/cello.wav"}}}
{"data":{"type":"command","id":"play","attributes":{"file":"/home/pi/projects/rpi-lighting-field/assets/audio/cello.wav"}}}
{"data":{"type":"command","id":"play","attributes":{"file":"/home/pi/projects/rpi-lighting-field/assets/audio/440-stereo.wav"}}}
{"data":[{"type":"command","id":"play"},{"type":"command","id":"stop"}]}
{"data":[{"type":"command","id":"play"},{"type":"command","id":"play"},{"type":"command","id":"stop"}]}
{"data":{"type":"command","id":"play"}}
{"data":{"type":"command","id":"play","attributes":{"file":"drums-01.wav"}}}
{"data":{"type":"command","id":"stop"}}
{"data":{"type":"command","id":"getCommands"}}
{"data":{"type":"illegal type","id":"illegal id"}}
{"data":{"type":"command","id":"removePlay"}}
{"data":[{"type":"command","id":"getCommands"},{"type":"command","id":"removePlay"}]}
{"data":{"type":"command","id":"getCommands"},{"type":"command","id":"removePlay"}}
{"data":[{"type":"command","id":"getCommands"},{"type":"command","id":"removePlay"},{"type":"command","id":"getCommands"},{"type":"command","id":"play"}]}
{"errors":[{"code":"code1","title":"title1","detail":"detail1"},{"code":"code2","title":"title2","detail":"detail2"}]}
{"errors":{"code":"code","title":"title","detail":"detail"}}
'''
