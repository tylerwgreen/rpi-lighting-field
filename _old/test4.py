#!/usr/bin/env python
# encoding: utf-8

from __future__ import division # required for float division, uses Python 3 division behavior

import wave
import time
import sys
import numpy
import pyaudio
import bisect
numpy.set_printoptions(threshold = numpy.nan)

class AudioAnalyzer:
	# CONFIG SETTINGS
	# streamFrameIterations = 0
	# streamFrameIterationsLimit = 100
	framesPerBuffer = 512 * 8 # the resolution of stream samples
	# CLASS VARS
	pyAudioInstance = None
	waveFileData = None
	waveFileFormat = None
	waveFileChannels = None
	waveFileFreqRate = None
	pyAudioStream = None # pyAudioInstance.open
	waveFileDataFramesData = [] # this needs to be set for the pyAudioStream thead to place data into
	fftDataHeaderPrinted = False
	octaveRanges = {
		'freq': [],
		'float': [], # used to separate freqs into octave buckets
		'noiseFloor': [],
		'ceiling': [
			# 6232,	# [20, 40]
			# 18375,	# [40, 80]
			# 15040,	# [80, 160]
			# 12343,	# [160, 320]
			# 5512,	# [320, 640]
			# 5148,	# [640, 1280]
			# 4163,	# [1280, 2560]
			# 3623,	# [2560, 5120]
			# 877,	# [5120, 10240]
			# 11		# [10240, 20000]
			
			1,	# [20, 40]
			1,	# [40, 80]
			1,	# [80, 160]
			1,	# [160, 320]
			1,	# [320, 640]
			1,	# [640, 1280]
			1,	# [1280, 2560]
			1,	# [2560, 5120]
			1,	# [5120, 10240]
			1	# [10240, 20000]
		]
	}
	
	# [20, 40],
	# [40, 80],
	# [80, 160],
	# [160, 320],
	# [320, 640],
	# [640, 1280],
	# [1280, 2560],
	# [2560, 5120],
	# [5120, 10240],
	# [10240, 20000]
	
	# WAVE FILES
	# waveFile = 'assets/0_16.wav' # single freq
	# waveFile = 'assets/tone.wav' # freq sweep
	# waveFile = 'assets/technologic.wav'
	waveFile = 'assets/technologic-real.wav'
	# waveFile = 'assets/drums-01.wav'
	# waveFile = 'assets/1k-octaves.wav'
	# waveFile = 'assets/440-octaves.wav'
	# waveFile = 'assets/440-stereo.wav' # 440 khz tone
	# waveFile = 'assets/440-mono.wav' # 440 khz tone
	# waveFile = 'assets/440-stereo-loud.wav'
	# waveFile = 'assets/440-mono-loud.wav'
	# waveFile = 'assets/440-mono-half-as-loud.wav' # 440 khz tone half as loud as 440-mono.wav
	# waveFile = 'assets/440-mono-quiet.wav' # 440 khz tone quieter than 440-mono.wav
	# waveFile = 'assets/440-mono-16-44-0db.wav' # 440 khz tone

	def __init__(self):
		print "INIT PYAUDIO START ----------"
		self.pyAudioInstance = pyaudio.PyAudio()
		print "INIT PYAUDIO END ----------\n\n"
		self.readWav()
		self.createOctaveRanges()
		self.configPyAudio()
		self.mainLoop()
	
	def createOctaveRanges(self):
		freqMin = 20
		freqMax = 20000
		freqCurrent = freqMin
		currentOctave = None
		while freqCurrent < freqMax:
			freqCurrentDoubled = freqCurrent * 2
			if freqCurrentDoubled > freqMax:
				freqCurrentDoubled = freqMax
			self.octaveRanges['freq'].append([freqCurrent, freqCurrentDoubled])
			self.octaveRanges['float'].append([freqCurrent / self.waveFileFreqRate, freqCurrentDoubled / self.waveFileFreqRate])
			freqCurrent = freqCurrentDoubled
		# print self.octaveRanges['freq']
		# sys.exit()
	
	def readWav(self):
		# ensure an audio file was passed as the second argument to python
		if len(sys.argv) < 2:
			# print 'Usage: python {} filename.wav'.format(sys.argv[0])
			waveFile = self.waveFile
		else:
			waveFile = sys.argv[0]
		self.waveFileData = wave.open(waveFile, 'rb') # rb for read only mode
		sampleWidth = self.waveFileData.getsampwidth()
		self.waveFileFormat = self.pyAudioInstance.get_format_from_width(
			width = sampleWidth # The desired sample width in bytes (1, 2, 3, or 4)
		)
		self.waveFileChannels = self.waveFileData.getnchannels()
		self.waveFileFreqRate = self.waveFileData.getframerate()
		bitRate = sampleWidth * 8
		print 'framesPerBuffer {framesPerBuffer} sampleWidth (bytes) {sampleWidth} format {format} channels {channels} freqRate {freqRate} bitRate {bitRate}'.format(
			framesPerBuffer = self.framesPerBuffer,
			sampleWidth = sampleWidth,
			format = self.waveFileFormat,
			channels = self.waveFileChannels,
			freqRate = self.waveFileFreqRate,
			bitRate = bitRate
		)
		if (bitRate) != 16:
			raise Exception('Wav file must be 16 bit, {bitRate} bit given'.format(bitRate = bitRate))
		if (self.waveFileFreqRate) != 44100:
			sys.exit('Wav file must be 44100, {sampleRate} given'.format(sampleRate = self.waveFileFreqRate))

	def configPyAudio(self):
		self.pyAudioStream = self.pyAudioInstance.open(
			# PA_manager,									# A reference to the managing PyAudio instance
			rate = self.waveFileFreqRate,					# Sampling rate
			channels = self.waveFileChannels,				# Number of channels
			format = self.waveFileFormat,					# Sampling size and format
			# input = True,									# Specifies whether this is an input stream. Defaults to False.
			output = True,									# Specifies whether this is an output stream. Defaults to False.
			# input_device_index = False,					# Index of Input Device to use. Unspecified (or None) uses default device. Ignored if input is False.
			# output_device_index = False,					# Index of Output Device to use. Unspecified (or None) uses the default device. Ignored if output is False.
			frames_per_buffer = self.framesPerBuffer,		# Specifies the number of frames per buffer.
			start = True,									# Start the stream running immediately. Defaults to True. In general, there is no reason to set this to False.
			# input_host_api_specific_stream_info,			# Specifies a host API specific stream information data structure for input.
			# output_host_api_specific_stream_info,			# Specifies a host API specific stream information data structure for output.
			stream_callback = self.pyAudioStreamCallback	# Specifies a callback function for non-blocking (callback) operation. Default is None, which indicates blocking operation (i.e., Stream.read() and Stream.write()).
			# Note: stream_callback is called in a separate thread (from the main thread). Exceptions that occur in the stream_callback will:
				# 1 print a traceback on standard error to aid debugging,
				# 2 queue the exception to be thrown (at some point) in the main thread, and
				# 3 return paAbort to PortAudio to stop the stream.
		)

	def mainLoop(self):
		while self.pyAudioStream.is_active():
			if len(self.waveFileDataFramesData) > 0:
				self.analyzeWaveFileDataFrames()
			# wait to check while again
			time.sleep(0.1)
		# Close the stream
		self.pyAudioStream.close()
		self.waveFileData.close()
		# Terminate PortAudio
		self.pyAudioInstance.terminate()
		# exit
		sys.exit('done')

	def pyAudioStreamCallback(
		self,
		in_data,		# recorded data if input = True; else None
		frame_count,	# number of frames
		time_info,		# a dictionary with the following keys: input_buffer_adc_time, current_time, and output_buffer_dac_time; see the PortAudio documentation for their meanings. status_flags is one of PortAutio Callback Flag.
		status			# PaCallbackFlags
		):
		dataFrames = self.waveFileData.readframes(frame_count)
		# should only ever run this program with 16 bit audio files
		dataInt = numpy.fromstring(dataFrames, dtype = numpy.int16)
		# break out channel data
		if self.waveFileChannels == 2:
			ch1 = dataInt[0::2]
			ch2 = dataInt[1::2]
		else:
			ch1 = dataInt
			ch2 = dataInt
		# only analyze one channel
		self.waveFileDataFramesData = ch1
		# handle iterations and return
		# if self.streamFrameIterations >= self.streamFrameIterationsLimit:
			# return (
				# dataFrames,		# a byte array whose length should be the (frame_count * channels * bytes-per-channel) if output = True or None if output = False.
				# pyaudio.paAbort	# must be either paContinue, paComplete or paAbort (one of PortAudio Callback Return Code). When output = True and out_data does not contain at least frame_count frames, paComplete is assumed for flag.
			# )
		# self.streamFrameIterations += 1
		return (
			dataFrames,			# a byte array whose length should be the (frame_count * channels * bytes-per-channel) if output = True or None if output = False.
			pyaudio.paContinue	# must be either paContinue, paComplete or paAbort (one of PortAudio Callback Return Code). When output = True and out_data does not contain at least frame_count frames, paComplete is assumed for flag.
		)

	def analyzeWaveFileDataFrames(self):
		fftData = numpy.fft.fft(self.waveFileDataFramesData) # The truncated or zero-padded input, transformed along the axis
		freqs = numpy.fft.fftfreq(len(fftData))
		# print len(fftData), len(freqs)
		# self.printFreqAmpPeak(fftData, freqs)
		# self.printFreqAmpAll(fftData, freqs)
		octavesAmplitudes = self.analyzeoctavesAmplitudes(fftData, freqs)
		self.printOctavesAmplitudes(octavesAmplitudes)
		# self.printOctaveAmplitudePeaks(octavesAmplitudes)
	
	def analyzeoctavesAmplitudes(self, fftData, freqs):
		# build octavesAmplitudes container
		octavesAmplitudes = []
		for octaveRange in self.octaveRanges['float']:
			octavesAmplitudes.append([])
		# print numpy.max(freqs)
		# return None
		for freqIdx, freq in enumerate(freqs):
			# no need to analyze the negative half of the wave
			# it is more accurate to analyze negative half
			# if freq < 0:
				# continue
			freq = abs(freq)
			amp = abs(fftData[freqIdx])
			# frequency ranges hard coded from self.octaveRanges['float']
			if                           freq <= 0.0009070294784580499:
				bucket = 0
				octavesAmplitudes[0].append(amp)
			elif 0.0009070294784580499 < freq <= 0.0018140589569160999:
				bucket = 1
				octavesAmplitudes[1].append(amp)
			elif 0.0018140589569160999 < freq <= 0.0036281179138321997:
				bucket = 2
				octavesAmplitudes[2].append(amp)
			elif 0.0036281179138321997 < freq <= 0.0072562358276643995:
				bucket = 3
				octavesAmplitudes[3].append(amp)
			elif 0.0072562358276643995  < freq <= 0.014512471655328799:
				bucket = 4
				octavesAmplitudes[4].append(amp)
			elif 0.014512471655328799   < freq <= 0.029024943310657598:
				bucket = 5
				octavesAmplitudes[5].append(amp)
			elif 0.029024943310657598   < freq <= 0.11609977324263039:
				bucket = 6
				octavesAmplitudes[6].append(amp)
			elif 0.11609977324263039   < freq <= 0.23219954648526078:
				bucket = 7
				octavesAmplitudes[7].append(amp)
			elif 0.23219954648526078   < freq <= 0.45351473922902497:
				bucket = 8
				octavesAmplitudes[8].append(amp)
			elif 0.45351473922902497   < freq:
				bucket = 9
				octavesAmplitudes[9].append(amp)
			else:
				bucket = 9
				octavesAmplitudes[9].append(amp)
			# self.printOctaveAmplitudeBuckets(freq, amp, bucket)
		# self.printOctaveAmplitudeComparisions(fftData, freqs, octavesAmplitudes)
		for octaveIdx, octaveAmplitudes in enumerate(octavesAmplitudes):
			octaveCeiling = self.octaveRanges['ceiling'][octaveIdx]
			octaveAmpMax = self.calculateAmplitude(numpy.max(octaveAmplitudes))
			octaveAmpMean = self.calculateAmplitude(numpy.mean(octaveAmplitudes))
			octaveAmpPercent = int(octaveAmpMean / octaveCeiling * 100)
			if octaveAmpMax > octaveCeiling:
				self.octaveRanges['ceiling'][octaveIdx] = octaveAmpMax
			octavesAmplitudes[octaveIdx] = octaveAmpPercent
		# print octavesAmplitudes
		# print self.octaveRanges['ceiling']
		return octavesAmplitudes
	
	def printOctaveAmplitudeBuckets(self, freq, amp, bucket):
		if freq < 0.45:
			return
		print('freq {freq} amp {amp} bucket {bucket}'.format(
			freq = freq,
			amp = self.calculateAmplitude(amp),
			bucket = bucket
		))
	
	def printOctaveAmplitudeComparisions(self, fftData, freqs, octavesAmplitudes):
		print('fftDataLen {fftDataLen} freqsLen {freqsLen} octavesAmplitudesLen {octavesAmplitudesLen}'.format(
			fftDataLen = len(fftData),
			freqsLen = len(freqs),
			octavesAmplitudesLen = sum(len(x) for x in octavesAmplitudes)
		))
	
	def printOctavesAmplitudes(self, octavesAmplitudes):
		print("0 {octave0}\n1 {octave1}\n2 {octave2}\n3 {octave3}\n4 {octave4}\n5 {octave5}\n6 {octave6}\n7 {octave7}\n8 {octave8}\n9 {octave9}\n".format(
			octave0 = self.renderOctavesAmplitudesLine(octavesAmplitudes[0]),
			octave1 = self.renderOctavesAmplitudesLine(octavesAmplitudes[1]),
			octave2 = self.renderOctavesAmplitudesLine(octavesAmplitudes[2]),
			octave3 = self.renderOctavesAmplitudesLine(octavesAmplitudes[3]),
			octave4 = self.renderOctavesAmplitudesLine(octavesAmplitudes[4]),
			octave5 = self.renderOctavesAmplitudesLine(octavesAmplitudes[5]),
			octave6 = self.renderOctavesAmplitudesLine(octavesAmplitudes[6]),
			octave7 = self.renderOctavesAmplitudesLine(octavesAmplitudes[7]),
			octave8 = self.renderOctavesAmplitudesLine(octavesAmplitudes[8]),
			octave9 = self.renderOctavesAmplitudesLine(octavesAmplitudes[9]),
		))
	
	def renderOctavesAmplitudesLine(self, amp):
		line = ''
		for i in range(0, int(amp / 10)):
			line += '-'
		return line
	
	def printOctaveAmplitudePeaks(self, octavesAmplitudes):
		print("0 {octave0}\n1 {octave1}\n2 {octave2}\n3 {octave3}\n4 {octave4}\n5 {octave5}\n6 {octave6}\n7 {octave7}\n8 {octave8}\n9 {octave9}\n".format(
			octave0 = self.calculateAmplitude(numpy.max(octavesAmplitudes[0])),
			octave1 = self.calculateAmplitude(numpy.max(octavesAmplitudes[1])),
			octave2 = self.calculateAmplitude(numpy.max(octavesAmplitudes[2])),
			octave3 = self.calculateAmplitude(numpy.max(octavesAmplitudes[3])),
			octave4 = self.calculateAmplitude(numpy.max(octavesAmplitudes[4])),
			octave5 = self.calculateAmplitude(numpy.max(octavesAmplitudes[5])),
			octave6 = self.calculateAmplitude(numpy.max(octavesAmplitudes[6])),
			octave7 = self.calculateAmplitude(numpy.max(octavesAmplitudes[7])),
			octave8 = self.calculateAmplitude(numpy.max(octavesAmplitudes[8])),
			octave9 = self.calculateAmplitude(numpy.max(octavesAmplitudes[9])),
		))
	
	# test sine waves to ensure accurate freq analyzation
	def printFreqAmpPeak(self, fftData, freqs):
		# Find the peak in the coefficients
		# feqIdx = numpy.argmax(numpy.abs(fftData))
		feqIdx = numpy.max(numpy.abs(fftData))
		freqHertz = self.calculateFreqHertz(freqs[feqIdx])
		amplitude = self.calculateAmplitude(fftData[feqIdx])
		print('freq {freqHertz} amp {amplitude}'.format(
			freqHertz = ('{:>6d}'.format(int(freqHertz))),
			amplitude = ('{:>9d}'.format(int(amplitude)))
		))
	
	# test sine waves to ensure accurate freq analyzation
	def printFreqAmpAll(self, fftData, freqs):
		for feqIdx, freq in enumerate(freqs):
			# no need to analyze the negative half of the wave
			# it is more accurate to analyze negative half
			# if freq < 0:
				# continue
			freqHertz = self.calculateFreqHertz(freq)
			amplitude = self.calculateAmplitude(fftData[feqIdx])
			print('freq {freqHertz} amp {amplitude}'.format(
				freqHertz = ('{:>6d}'.format(int(freqHertz))),
				amplitude = ('{:>9d}'.format(int(amplitude)))
			))
	
	def calculateFreqHertz(self, freq):
		return abs((freq * self.waveFileFreqRate) / self.waveFileChannels)
	
	def calculateAmplitude(self, amp):
		return int(abs(amp / self.waveFileChannels) / 1000)
		# return int(abs(amp / self.waveFileChannels) / (self.waveFileFreqRate / 10))
		# return int(abs(amp / self.waveFileChannels))

if __name__ == "__main__":
	aa = AudioAnalyzer()