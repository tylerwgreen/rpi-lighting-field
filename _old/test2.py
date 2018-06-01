#!/usr/bin/env python
# encoding: utf-8

## Module infomation ###
# Python (3.4.4)
# numpy (1.10.2)
# PyAudio (0.2.9)
# matplotlib (1.5.1)
# All 32bit edition
########################

import numpy as np
import pyaudio
import wave
import sys

import matplotlib.pyplot as plt

class SpectrumAnalyzer:
	FORMAT = pyaudio.paFloat32
	CHANNELS = 2
	RATE = 44100
	CHUNK = 512
	START = 0
	N = 512

	wave_x = 0
	wave_y = 0
	spec_x = 0
	spec_y = 0
	data = []

	def __init__(self):
		self.pa = pyaudio.PyAudio()
		self.openWav()
		self.stream = self.pa.open(format = self.FORMAT,
			channels = self.CHANNELS, 
			rate = self.RATE, 
			input = False,
			output = True,
			frames_per_buffer = self.CHUNK)
		# Main loop
		self.loop()

	def loop(self):
		try:
			while True :
				# self.data = self.audioinput()
				self.data = self.readWav()
				# self.fft()
				# self.graphplot()

		except KeyboardInterrupt:
			self.pa.close()

		print("End...")

	# def audioinput(self):
		# ret = self.stream.read(self.CHUNK)
		# ret = np.fromstring(ret, np.float32)
		# return ret
	
	def openWav(self):
		if len(sys.argv) < 2:
			waveFile = 'assets/0_16.wav'
		else:
			waveFile = sys.argv[0]
		self.wf = wave.open(waveFile, 'rb')
	
	def readWav(self):
		data = self.wf.readframes(self.CHUNK)
		
		self.stream.write(data)
		return data

	def fft(self):
		self.wave_x = range(self.START, self.START + self.N)
		self.wave_y = self.data[self.START:self.START + self.N]
		self.spec_x = np.fft.fftfreq(self.N, d = 1.0 / self.RATE)  
		y = np.fft.fft(self.data[self.START:self.START + self.N])	
		self.spec_y = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in y]

	def graphplot(self):
		plt.clf()
		# wave
		plt.subplot(311)
		plt.plot(self.wave_x, self.wave_y)
		plt.axis([self.START, self.START + self.N, -0.5, 0.5])
		plt.xlabel("time [sample]")
		plt.ylabel("amplitude")
		#Spectrum
		plt.subplot(312)
		plt.plot(self.spec_x, self.spec_y, marker= 'o', linestyle='-')
		plt.axis([0, self.RATE / 2, 0, 50])
		plt.xlabel("frequency [Hz]")
		plt.ylabel("amplitude spectrum")
		#Pause
		plt.pause(.01)

if __name__ == "__main__":
	spec = SpectrumAnalyzer()