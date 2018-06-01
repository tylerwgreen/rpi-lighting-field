#!/usr/bin/env python
# encoding: utf-8

import sys
import os
# from StdoutSupressor import StdoutSupressor
from NodeInterface import NodeInterface
from AudioAnalyzer import AudioAnalyzer

class App:

	# stdoutSupressor = None
	# nodeInterface = None
	# audioAnalyzer = None

	def __init__(self):
		# configure dependencies
		self.stdoutSupressor = StdoutSupressor(sys, os)
		self.nodeInterface = NodeInterface()
		self.registerNodeInterfaceCommands()
		# configure audioAnalyzer and suppress warning/errors
		self.stdoutSupressor.supress()
		self.audioAnalyzer = AudioAnalyzer(
			self.nodeInterface,
			self.stdoutSupressor
		)
		self.stdoutSupressor.restore()
		# App is configured, start the main loop
		self.nodeInterface.message(self.stdoutSupressor.flush())
		self.nodeInterface.message('App.__init__ success')
		self.mainLoop()

	def mainLoop(self):
		while True:
			self.nodeInterface.listen()
	
	def registerNodeInterfaceCommands(self):
		# these are commands that can be called from node
		self.nodeInterface.registerCommand('play', self.play)
		self.nodeInterface.registerCommand('stop', self.stop)
	
	def play(self, data):
		self.audioAnalyzer.play(data['file'])
		self.nodeInterface.message('App.play success')

	def stop(self):
		self.audioAnalyzer.stop()
		self.nodeInterface.message('App.stop success')

if __name__ == '__main__':
	app = App()

'''
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