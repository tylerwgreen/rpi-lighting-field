#!/usr/bin/env python

import sys
import json

class NodeInterface:

	commands = {}
	
	def registerCommand(self, commandId, command):
		self.commands[commandId] = command
	
	def removeCommand(self, commandId):
		if commandId in self.commands:
			self.commands.pop(commandId, None)
	
	def getCommands(self):
		return self.commands
	
	def listen(self):
		line = sys.stdin.readline()
		if len(line) > 0:
			jsonData = self._decodeJson(line)
			if 'errors' in jsonData:
				errors = jsonData['errors']
				if isinstance(errors, list):
					_errors = []
					for _error in errors:
						_errors.append(_error['detail'])
					error = '|'.join(_errors)
				else:
					error = errors['detail']
				self._handleException(Exception, 'listen errors', error)
			elif 'data' in jsonData:
				data = jsonData['data']
				if isinstance(data, list):
					for _data in data:
						self._handleData(_data)
				else:
					self._handleData(data)
			else:
				self._handleException(Exception, 'listen errors', 'Json input does not contain data or errors')
	
	def _handleData(self, data):
		if 'command' == data['type']:
			commandId = data['id']
			if commandId in self.commands:
				attributes = {}
				if 'attributes' in data:
					attributes = data['attributes']
				try:
					result = self.commands[commandId](attributes)
				except Exception, error:
					self._handleException(Exception, '_handleData command ({command})'.format(command = commandId), error)
				else:
					self._success({
						'type': 'command',
						'id': commandId,
						'attributes': {
							'result': result
						}
					})
			else:
				self._error(
					0,
					'Unregistered command',
					'Json input contained unregistered command: {}'.format(commandId)
				)
		else:
			self._error(
				0,
				'Unknown input',
				'Json input contained unknown data type: {}'.format(data['type'])
			)

	def _success(self, data):
		self._printJson({'data': [data]})
	
	def _error(self, code, title, detail):
		self._printJson({'errors': [{
			'code': code,
			'title': title,
			'detail': detail,
		}]})
	
	def _decodeJson(self, str):
		try:
			jsonDecoded = json.loads(str)
		except Exception, error:
			self._handleException(Exception, '_decodeJson', error)
		else:
			return jsonDecoded
	
	def _encodeJson(self, data):
		try:
			jsonEncoded = json.dumps(data)
		except Exception, error:
			self._handleException(Exception, '_encodeJson', error)
		else:
			return jsonEncoded
	
	def _printJson(self, data):
		print self._encodeJson(data)
		sys.stdout.flush()
	
	def _handleException(self, Exception, context, error):
		sys.exit('Exception: {context} - {error}'.format(context = context, error = error))
	
	def message(self, message):
		self._printJson({'data': {
			'type': 'message',
			'id': None,
			'attributes': {
				'content': message
			}
		}})
		
	def audioPeaks(self, id, data):
		self._printJson({'data': {
			'type': 'audioPeaks',
			'id': id,
			'attributes': {
				'data': data
			}
		}})