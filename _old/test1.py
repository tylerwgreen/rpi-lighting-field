#!/usr/bin/env python
# encoding: utf-8

import wave
import time
import sys
import struct
import numpy
import pyaudio
# import matplotlib
# matplotlib.use('AGG')
# import matplotlib.pyplot as pyplot

import math

class SpectrumAnalyzer:
	streamFrameIterations = 0
	streamFrameIterationsLimit = 100
	framesPerBuffer = 512 * 16 # the resolution of stream samples
	# START = 0
	# N = 512 * 2

	# wave_x = 0
	# wave_y = 0
	# spec_x = 0
	# spec_y = 0
	data = []

	def __init__(self):
		self.makeWav()
		# self.testWav()
		# self.plotTest()
		# self.plotTestTwo()
		sys.exit()
		
		
		self.pyAudioInstance = pyaudio.PyAudio()
		self.readWav()
		self.configPyAudio()
		self.loop() # Main loop

	def makeWav(self):
		# http://stackoverflow.com/questions/3637350/how-to-write-stereo-wav-files-in-python
		# http://www.sonicspot.com/guide/wavefiles.html
		freq = 440.0
		data_size = 100000
		# fname = "assets/440-mono-loud.wav"
		fname = "assets/440-stereo-loud.wav"
		frate = 44100.0
		amp = 65500.0 # loudest I could get to render
		# amp = 64000.0
		# amp = 8000.0
		nchannels = 2
		sampwidth = 2
		framerate = int(frate)
		nframes = data_size
		comptype = "NONE"
		compname = "not compressed"
		data = [math.sin(2 * math.pi * freq * (x / frate))
			for x in range(data_size)]
		wav_file = wave.open(fname, 'w')
		wav_file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))
		for v in data:
			wav_file.writeframes(struct.pack('h', int(v * amp / 2)))
		wav_file.close()

	def testWav(self):
		data_size = 100000
		fname = "assets/440-mono.wav"
		# fname = "assets/440-stereo.wav"
		frate = 44100.0
		wav_file = wave.open(fname, 'r')
		data = wav_file.readframes(data_size)
		wav_file.close()
		data = struct.unpack('{n}h'.format(n=data_size), data)
		data = numpy.array(data)

		w = numpy.fft.fft(data)
		freqs = numpy.fft.fftfreq(len(w))
		print(freqs.min(), freqs.max())
		# (-0.5, 0.499975)

		# Find the peak in the coefficients
		idx = numpy.argmax(numpy.abs(w))
		freq = freqs[idx]
		freq_in_hertz = abs(freq * frate)
		print(freq_in_hertz)
		# 439.8975
	
	def readWav(self):
		# ensure an audio file was passed as the second argument to python
		if len(sys.argv) < 2:
			# print 'Usage: python {} filename.wav'.format(sys.argv[0])
			# waveFile = 'assets/0_16.wav' # single freq
			# waveFile = 'assets/tone.wav' # freq sweep
			# waveFile = 'assets/technologic.wav'
			# waveFile = 'assets/drums-01.wav'
			# waveFile = 'assets/1k-octaves.wav'
			# waveFile = 'assets/440-octaves.wav'
			waveFile = 'assets/440-stereo.wav' # 440 khz tone
			# waveFile = 'assets/440-mono.wav' # 440 khz tone
		else:
			waveFile = sys.argv[0]
		self.waveFile = wave.open(waveFile, 'rb')
		self.sampleWidth = self.waveFile.getsampwidth()
		self.format = self.pyAudioInstance.get_format_from_width(
			width = self.sampleWidth # The desired sample width in bytes (1, 2, 3, or 4)
		)
		self.channels = self.waveFile.getnchannels()
		self.rate = self.waveFile.getframerate() # frequency
		print 'framesPerBuffer {} sampleWidth {} format {} channels {} rate {}'.format(
			self.framesPerBuffer,
			self.sampleWidth,
			self.format,
			self.channels,
			self.rate
		)

	def configPyAudio(self):
		self.pyAudioStream = self.pyAudioInstance.open(
			# PA_manager,								# A reference to the managing PyAudio instance
			rate=self.rate,								# Sampling rate
			channels=self.channels,						# Number of channels
			format=self.format,							# Sampling size and format
			# input=True,								# Specifies whether this is an input stream. Defaults to False.
			output=True,								# Specifies whether this is an output stream. Defaults to False.
			# input_device_index=False,					# Index of Input Device to use. Unspecified (or None) uses default device. Ignored if input is False.
			# output_device_index=False,				# Index of Output Device to use. Unspecified (or None) uses the default device. Ignored if output is False.
			frames_per_buffer=self.framesPerBuffer,		# Specifies the number of frames per buffer.
			start=True,									# Start the stream running immediately. Defaults to True. In general, there is no reason to set this to False.
			# input_host_api_specific_stream_info,		# Specifies a host API specific stream information data structure for input.
			# output_host_api_specific_stream_info,		# Specifies a host API specific stream information data structure for output.
			stream_callback=self.pyAudioStreamCallback	# Specifies a callback function for non-blocking (callback) operation. Default is None, which indicates blocking operation (i.e., Stream.read() and Stream.write()).
			# Note: stream_callback is called in a separate thread (from the main thread). Exceptions that occur in the stream_callback will:
				# 1 print a traceback on standard error to aid debugging,
				# 2 queue the exception to be thrown (at some point) in the main thread, and
				# 3 return paAbort to PortAudio to stop the stream.
		)

	def loop(self):
		while self.pyAudioStream.is_active():
			# print self.data
			if len(self.data) > 0:
				# self.plot()
				# self.plotTest()
				self.fft()
				# self.graphplot()
			time.sleep(0.1)
		# Close the stream
		self.pyAudioStream.close()
		self.waveFile.close()
		# Terminate PortAudio
		self.pyAudioInstance.terminate()
		# exit
		sys.exit('done')

	def pyAudioStreamCallback(
		self,
		in_data,		# recorded data if input=True; else None
		frame_count,	# number of frames
		time_info,		# a dictionary with the following keys: input_buffer_adc_time, current_time, and output_buffer_dac_time; see the PortAudio documentation for their meanings. status_flags is one of PortAutio Callback Flag.
		status			# PaCallbackFlags
		):
		data = self.waveFile.readframes(frame_count)
		# dataInt = numpy.fromstring(data, dtype=numpy.int16)
		# dataInt = numpy.fromstring(data, dtype=numpy.float32)

		# break out channel data
		if self.channels == 2:
			dataInt = numpy.fromstring(data, dtype=numpy.int16)
			ch1 = dataInt[0::2]
			ch2 = dataInt[1::2]
		else:
			dataInt = numpy.fromstring(data, dtype=numpy.int16)
			ch1 = dataInt
			ch2 = dataInt
		# print 'ch1Max {} ch1Min {} '.format(
			# ('{:>6d}'.format(int(max(ch1)))),
			# ('{:>6d}'.format(int(min(ch1))))
		# )
		# only analyze one channel
		# self.data = ch1
		self.data = dataInt
		# print 'channels {} framesPerBuffer {} dataLen {} dataIntLen {} ch1Len {} ch2Len {}'.format(
			# self.channels,
			# self.framesPerBuffer,
			# len(data),
			# len(dataInt),
			# len(ch1),
			# len(ch2)
		# )
		
		
		# data = struct.unpack('{n}h'.format(n=frame_count * self.channels), data)
		# data = numpy.array(data)

		# w = numpy.fft.fft(data)
		# freqs = numpy.fft.fftfreq(len(w))
		# print(freqs.min(), freqs.max())
		# # (-0.5, 0.499975)

		# # Find the peak in the coefficients
		# idx = numpy.argmax(numpy.absolute(w))
		# freq = freqs[idx]
		# freq_in_hertz = numpy.absolute(freq * self.rate)
		# print(freq_in_hertz)
		# # 439.8975
		
		# handle iterations and return
		if self.streamFrameIterations >= self.streamFrameIterationsLimit:
			return (
				data,			# a byte array whose length should be the (frame_count * channels * bytes-per-channel) if output=True or None if output=False.
				pyaudio.paAbort	# must be either paContinue, paComplete or paAbort (one of PortAudio Callback Return Code). When output=True and out_data does not contain at least frame_count frames, paComplete is assumed for flag.
			)
		self.streamFrameIterations += 1
		return (
			data,				# a byte array whose length should be the (frame_count * channels * bytes-per-channel) if output=True or None if output=False.
			pyaudio.paContinue	# must be either paContinue, paComplete or paAbort (one of PortAudio Callback Return Code). When output=True and out_data does not contain at least frame_count frames, paComplete is assumed for flag.
		)

	def plot(self):
		fig, ax = pyplot.subplots()
		ax.plot(self.data, '-')
		pyplot.show()
		
	# def plotTest(self):
		# # pyplot.show()
		# pyplot.ion()
		# # fig = pyplot.figure()
		# # ax = fig.add_subplot(111)
		# fig, ax = pyplot.subplots()
		# x = numpy.arange(0, self.framesPerBuffer)
		# # print(x)
		# line, = ax.plot(x, numpy.random.rand(self.framesPerBuffer))
		# # print(line)
		# # sys.exit();
		# ax.set_ylim(0, 512)
		# ax.set_xlim(0, self.framesPerBuffer)
		
		# while True:
			# line.set_ydata(self.data)
			# fig.canvas.draw()
			# fig.canvas.flush_events()

	# def plotTestTwo(self):
		# x = numpy.linspace(0, 6*numpy.pi, 100)
		# y = numpy.sin(x)

		# # You probably won't need this if you're embedding things in a tkinter plot...
		# pyplot.ion()

		# fig = pyplot.figure()
		# ax = fig.add_subplot(111)
		# line1, = ax.plot(x, y, 'r-') # Returns a tuple of line objects, thus the comma

		# for phase in numpy.linspace(0, 10*numpy.pi, 500):
			# line1.set_ydata(numpy.sin(x + phase))
			# fig.canvas.draw()
			# fig.canvas.flush_events()

	def fftTest(self):
		# w = numpy.fft.fft(self.data)
		w = numpy.fft.fft(self.data)
		freqs = numpy.fft.fftfreq(len(w))
		print(freqs.min(), freqs.max())
		# (-0.5, 0.499975)

		# Find the peak in the coefficients
		idx = numpy.argmax(numpy.abs(w))
		freq = freqs[idx]
		freq_in_hertz = abs(freq * self.rate)
		# freq_in_hertz = abs(freq * 22050)
		print(freq_in_hertz)
		# 439.8975

	def fft(self):
		self.fftTest()
		return None
		# 10240
		#  5120
		#  2560
		#  1280
		#   640
		#   320
		#   160
		#    80
		#    40
		#    20
		# return None
		# self.wave_x = range(self.START, self.START + self.N)
		# self.wave_y = self.data[self.START:self.START + self.N]
		self.spec_x = numpy.fft.fftfreq(self.framesPerBuffer, d = 1.0 / self.rate) 
		y = numpy.fft.fft(self.data[0:0 + self.framesPerBuffer])
		self.spec_y = [numpy.sqrt(c.real ** 2 + c.imag ** 2) for c in y]
		# print self.spec_x
		print 'yMax {} yMin {} xMax {} xMin {}'.format(
			('{:>12d}'.format(int(max(self.spec_y)))),
			('{:>12d}'.format(int(min(self.spec_y)))),
			('{:>12d}'.format(int(max(self.spec_x + self.rate / 2)))),
			('{:>12d}'.format(int(min(self.spec_x + self.rate / 2))))
			# str(max(self.spec_y)).zfill(10),
			# str(min(self.spec_y)).zfill(10),
			# str(max(self.spec_x)).zfill(10),
			# str(min(self.spec_x)).zfill(10)
		)
		# sys.exit();
		# print "amp {} freq {}".format(self.spec_y[20], self.spec_x[20])

	def graphplot(self):
		pyplot.clf()
		# wave
		# pyplot.subplot(311)
		# pyplot.plot(self.wave_x, self.wave_y)
		# pyplot.axis([self.START, self.START + self.N, -0.5, 0.5])
		# pyplot.xlabel("time [sample]")
		# pyplot.ylabel("amplitude")
		#Spectrum
		pyplot.subplot(312)
		pyplot.plot(self.spec_x, self.spec_y, marker= 'o', linestyle='-')
		pyplot.axis([0, self.rate / 2, 0, 50])
		pyplot.xlabel("frequency [Hz]")
		pyplot.ylabel("amplitude spectrum")
		#Pause
		pyplot.pause(.01)

if __name__ == "__main__":
	spec = SpectrumAnalyzer()