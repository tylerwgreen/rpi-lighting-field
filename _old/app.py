#!/usr/bin/env python

import sys
from app.modules.NodeInterface import NodeInterface

class App:

	nodeInterface = None
	interval = 0

	def __init__(self):
		# sys.exit()
		self.nodeInterface = NodeInterface()
		self.registerNodeInterfaceCommands()
		self.mainLoop()
	
	def mainLoop(self):
		while True:
			self.nodeInterface.listen()
			self.interval += 1
	
	def registerNodeInterfaceCommands(self):
		self.nodeInterface.registerCommand('play', self.play)
		self.nodeInterface.registerCommand('removePlay', self.removePlay)
		self.nodeInterface.registerCommand('stop', self.stop)
		self.nodeInterface.registerCommand('getCommands', self.getCommands)
		self.nodeInterface.registerCommand('getInterval', self.getInterval)
	
	def play(self):
		return {'foo':'bar','bar':'play success','foobar':1}
		
	def removePlay(self):
		self.nodeInterface.removeCommand('play')
		return 'removePlay success'

	def stop(self):
		raise Exception('stop error')
	
	def getCommands(self):
		registeredCommands = self.nodeInterface.getCommands()
		return list(registeredCommands.keys())

	def getInterval(self):
		return self.interval

if __name__ == '__main__':
	app = App()

'''
{"data":[{"type":"command","id":"play"},{"type":"command","id":"stop"}]}
{"data":[{"type":"command","id":"play"},{"type":"command","id":"play"},{"type":"command","id":"stop"}]}
{"data":{"type":"command","id":"play"}}
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