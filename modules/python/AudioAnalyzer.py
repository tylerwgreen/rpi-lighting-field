#!/usr/bin/env python
# encoding: utf-8

from __future__ import division # required for float division, uses Python 3 division behavior

import wave
import time
import sys
import os
import numpy
import pyaudio
import bisect
import logging
numpy.set_printoptions(threshold = numpy.nan)

from StdoutSupressor import StdoutSupressor

#logOctaveRanges() - Octaves: 10
#   20    40 [0.00045351473922902497, 0.0009070294784580499]
#   40    80 [0.0009070294784580499, 0.0018140589569160999]
#   80   160 [0.0018140589569160999, 0.0036281179138321997]
#  160   320 [0.0036281179138321997, 0.0072562358276643995]
#  320   640 [0.0072562358276643995, 0.014512471655328799]
#  640  1280 [0.014512471655328799, 0.029024943310657598]
# 1280  2560 [0.029024943310657598, 0.058049886621315196]
# 2560  5120 [0.058049886621315196, 0.11609977324263039]
# 5120 10240 [0.11609977324263039, 0.23219954648526078]
#10240 20000 [0.23219954648526078, 0.45351473922902497]

class AudioAnalyzer:
	# CONFIG SETTINGS
	framesPerBuffer = 1000 * 2 # the resolution of stream samples
	# CLASS VARS
	pyAudioInstance = None
	waveFileData = None
	waveFileFormat = None
	waveFileChannels = None
	waveFileFreqRate = None
	pyAudioStream = None # pyAudioInstance.open
	waveFileDataFramesData = [] # this needs to be set for the pyAudioStream thead to place data into
	octaveRanges = {
		'freq': [],
		'float': [], # used to separate freqs into octave buckets
	}

	def __init__(self, nodeInterface):
		self.nodeInterface = nodeInterface
		self.logger = logging.getLogger(__name__)
		self.stdoutSupressor = StdoutSupressor(sys, os)
		self.stdoutSupressor.supress()
		self.pyAudioInstance = pyaudio.PyAudio()
		self.stdoutSupressor.restore()
	
	# @profile
	def play(self, file):
		self.waveFile = file
		self.readWav()
		self.createOctaveRanges()
		self.configPyAudio()
		self.mainLoop()

	# reads, analyzes and validates wav audio file
	def readWav(self):
		self.waveFileData = wave.open(self.waveFile, 'rb') # rb for read only mode
		sampleWidth = self.waveFileData.getsampwidth()
		self.waveFileFormat = self.pyAudioInstance.get_format_from_width(
			width = sampleWidth # The desired sample width in bytes (1, 2, 3, or 4)
		)
		self.waveFileChannels = self.waveFileData.getnchannels()
		self.waveFileFreqRate = self.waveFileData.getframerate()
		bitRate = sampleWidth * 8
		# log wave info
		self.logger.info('readWav(): framesPerBuffer {framesPerBuffer} sampleWidth (bytes) {sampleWidth} format {format} channels {channels} freqRate {freqRate} bitRate {bitRate}'.format(
			framesPerBuffer = self.framesPerBuffer,
			sampleWidth = sampleWidth,
			format = self.waveFileFormat,
			channels = self.waveFileChannels,
			freqRate = self.waveFileFreqRate,
			bitRate = bitRate
		))
		if (bitRate) != 16:
			raise Exception('Wav file must be 16 bit, {bitRate} bit given'.format(bitRate = bitRate))
		if (self.waveFileFreqRate) != 44100:
			sys.exit('Wav file must be 44100, {sampleRate} given'.format(sampleRate = self.waveFileFreqRate))

	# creates octave ranges in freq and float values for audible spectrum
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
		# self.printOctaveRanges()

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

	# @profile
	def pyAudioStreamCallback(
		self,
		in_data,		# recorded data if input = True; else None
		frame_count,	# number of frames
		time_info,		# a dictionary with the following keys: input_buffer_adc_time, current_time, and output_buffer_dac_time; see the PortAudio documentation for their meanings. status_flags is one of PortAutio Callback Flag.
		status			# PaCallbackFlags
	):
		dataFrames = self.waveFileData.readframes(frame_count)
		# should only ever run this program with 16 bit audio files (validated in readWav function)
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
		return (
			dataFrames,			# a byte array whose length should be the (frame_count * channels * bytes-per-channel) if output = True or None if output = False.
			pyaudio.paContinue	# must be either paContinue, paComplete or paAbort (one of PortAudio Callback Return Code). When output = True and out_data does not contain at least frame_count frames, paComplete is assumed for flag.
		)
	
	# @profile
	def mainLoop(self):
		while self.pyAudioStream.is_active():
			if len(self.waveFileDataFramesData) > 0:
				self.analyzeWaveFileDataFrames()
			else:
				# wait to check while again
				time.sleep(.1)
		# Close the stream
		self.pyAudioStream.close()
		self.waveFileData.close()
		# Terminate pyAudio
		self.pyAudioInstance.terminate()
		# exit
		self.nodeInterface.audioComplete(None, True)
		# sys.exit()

	# @profile
	def analyzeWaveFileDataFrames(self):
		fftData = numpy.fft.fft(self.waveFileDataFramesData) # The truncated or zero-padded input, transformed along the axis
		freqs = numpy.fft.fftfreq(len(fftData))
		# print len(fftData), len(freqs) # they should be equal unless at the end of the stream/frames
		# self.printFreqAmpPeak(fftData, freqs)
		# self.printFreqAmpAll(fftData, freqs)
		octavesAmplitudes = self.analyzeoctavesAmplitudes(fftData, freqs)
		self.printOctavesAmplitudesJson(octavesAmplitudes)
		# self.printOctavesAmplitudes(octavesAmplitudes)
		# self.printOctaveAmplitudePeaks(octavesAmplitudes)
	
	# @profile
	def analyzeoctavesAmplitudes(self, fftData, freqs):
		# build octavesAmplitudes container
		# profiling revealed it's faster to define buckets rather than build with a loop
		octavesAmplitudes = [
			[],
			[],
			[],
			[],
			[],
			[],
			[],
			[],
			[],
			[],
		]
		# profiling revealed it was indeed faster to throw away the negative half of the wave form
		# no need to analyze the negative half of the wave although it may be more accurate to analyze
		# however, since we are using the freq index to find the amp for the freq, this will not work
		# freqs = [item for item in freqs if item >= 0]
		# profiling revealed this was fastest way to get index
		for freqIdx, freq in enumerate(freqs):
			if freq <= 0:
				continue
			octavesAmplitudes[self.getFreqBucketTopDown(freq)].append(abs(fftData[freqIdx]))
		# self.printOctaveAmplitudeComparisions(fftData, freqs, octavesAmplitudes)
		# profiling showed removing the loop was faster, just list manually
		
		# octavesAmplitudes[0] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[0]))
		# octavesAmplitudes[1] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[1]))
		# octavesAmplitudes[2] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[2]))
		# octavesAmplitudes[3] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[3]))
		# octavesAmplitudes[4] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[4]))
		# octavesAmplitudes[5] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[5]))
		# octavesAmplitudes[6] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[6]))
		# octavesAmplitudes[7] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[7]))
		# octavesAmplitudes[8] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[8]))
		# octavesAmplitudes[9] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[9]))
		
		# linearized to match pink noise
		octavesAmplitudes[0] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[0])) / 34
		octavesAmplitudes[1] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[1])) / 22
		octavesAmplitudes[2] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[2])) / 15
		octavesAmplitudes[3] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[3])) / 10
		octavesAmplitudes[4] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[4])) / 7
		octavesAmplitudes[5] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[5])) / 5
		octavesAmplitudes[6] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[6])) / 2.7
		octavesAmplitudes[7] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[7])) / 1.7
		octavesAmplitudes[8] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[8])) / 1.2
		octavesAmplitudes[9] = self.calculateAmplitude(numpy.mean(octavesAmplitudes[9]))
		return octavesAmplitudes

	def getFreqBucketTopDown(self, freq):
		# profiling revealed comparing a shorter num was not faster
		# because there is more data in the upper freqs, compare those first
		if	freq > 0.45351473922902497:
			return 9
		elif	freq > 0.23219954648526078:
			return 8
		elif	freq > 0.11609977324263039:
			return 7
		elif	freq > 0.029024943310657598:
			return 6
		elif	freq > 0.014512471655328799:
			return 5
		elif	freq > 0.0072562358276643995:
			return 4
		elif	freq > 0.0036281179138321997:
			return 3
		elif	freq > 0.0018140589569160999:
			return 2
		elif	freq > 0.0009070294784580499:
			return 1
		else:
			return 0

	# CALCULATIONS
	
	def calculateFreqHertz(self, freq):
		return int(abs((freq * self.waveFileFreqRate) / self.waveFileChannels))
	
	def calculateAmplitude(self, amp):
		return int((amp / self.waveFileChannels) / 100)
		# return int((amp / self.waveFileChannels) / 1000)

	# PRINT FUNCTIONS
	
	def printOctavesAmplitudesJson(self, octavesAmplitudes):
		self.nodeInterface.audioPeaks(None, octavesAmplitudes)
	
	# ensure freqs are going into the correct buckets
	def printOctaveAmplitudeBuckets(self, freq, amp, bucket):
		if freq < 0.45:
			return
		print('freq {freq} amp {amp} bucket {bucket}'.format(
			freq = freq,
			amp = self.calculateAmplitude(amp),
			bucket = bucket
		))
	
	# ensure the same amount of data exists for fftData, freqs and octavesAmplitudes
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
		freqIdx = numpy.argmax(numpy.abs(fftData))
		freqHertz = self.calculateFreqHertz(freqs[freqIdx])
		amplitude = self.calculateAmplitude(fftData[freqIdx])
		print('printFreqAmpPeak() - freq {freqHertz} amp {amplitude}'.format(
			freqHertz = ('{:>6d}'.format(int(freqHertz))),
			amplitude = ('{:>9d}'.format(int(amplitude)))
		))
	
	# test sine waves to ensure accurate freq analyzation
	def printFreqAmpAll(self, fftData, freqs):
		for freqIdx, freq in enumerate(freqs):
			freqHertz = self.calculateFreqHertz(freq)
			amplitude = self.calculateAmplitude(fftData[freqIdx])
			print('freq {freqHertz} amp {amplitude}'.format(
				freqHertz = ('{:>6d}'.format(int(freqHertz))),
				amplitude = ('{:>9d}'.format(int(amplitude)))
			))

	def printOctaveRanges(self):
		out = 'Octaves: ' + str(len(self.octaveRanges['freq'])) + '\n'
		for idx, freqs in enumerate(self.octaveRanges['freq']):
			out += '{} {} {}\n'.format(
				str(freqs[0]).rjust(5, ' '),
				str(freqs[1]).rjust(5, ' '),
				self.octaveRanges['float'][idx]
				
			)
		print('printOctaveRanges() - ' + out);
	