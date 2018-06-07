#!/usr/bin/env python
# encoding: utf-8

import logging
from cStringIO import StringIO

class StdoutSupressor():
	
	def __init__(self, sys, os):
		self.os = os
		self.sys = sys
		self.logger = logging.getLogger(__name__)
	
	def supress(self):
		self.data = None
		self.null_fds = [self.os.open(self.os.devnull, self.os.O_RDWR) for x in xrange(2)]
		self.save = self.os.dup(1), self.os.dup(2)
		self.os.dup2(self.null_fds[0], 1)
		self.os.dup2(self.null_fds[1], 2)
		self.old_stdout = self.sys.stdout
		self.sys.stdout = self.mystdout = StringIO()

	def restore(self):
		self.os.dup2(self.save[0], 1)
		self.os.dup2(self.save[1], 2)
		self.os.close(self.null_fds[0])
		self.os.close(self.null_fds[1])
		self.sys.stdout = self.old_stdout
		self.data = self.mystdout.getvalue()
		if len(self.data) > 0:
			self.logger.info(['suppressed', self.data])

	def flush(self):
		return self.data