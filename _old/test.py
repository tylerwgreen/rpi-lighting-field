import pyaudio
import wave
import time
import sys
import struct
import numpy

# import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig, ax = plt.subplots()

# import os
# print os.environ.get('DISPLAY','')
# sys.exit('foo');

# sys.argv[0] = name of file passed to python commmand
# sys.argv[1] = audio file passed to python command

# ensure an audio file was passed as the second argument to python
if len(sys.argv) < 2:
	print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
	sys.exit(-1)

waveFile = sys.argv[1]
waveFile = wave.open(waveFile, 'rb')

pyAudioInstance = pyaudio.PyAudio()

streamFrameIterations = 0

def pyAudioStreamCallback(
	in_data,		# recorded data if input=True; else None
	frame_count,	# number of frames
	time_info,		# a dictionary with the following keys: input_buffer_adc_time, current_time, and output_buffer_dac_time; see the PortAudio documentation for their meanings. status_flags is one of PortAutio Callback Flag.
	status			# PaCallbackFlags
):
	global streamFrameIterations, framesPerBuffer, channels, ax
	data = waveFile.readframes(frame_count)
	# print str(len(data))
	# multiplier = framesPerBuffer / len(data)
	# data_int = struct.unpack(str(len(data)) + 'B', data)
	# data_int = struct.unpack(str(len(data)) + 'B', data)
	dataInt = numpy.fromstring(data, dtype=numpy.int16)
	# break out channel data
	ch1 = dataInt[0::2]
	ch2 = dataInt[1::2]
	print 'channels {} framesPerBuffer {} dataLen {} dataIntLen {} ch1Len {} ch2Len {}'.format(channels, framesPerBuffer, len(data), len(dataInt), len(ch1), len(ch2))
	ax.plot(ch1, '-')
	# print dataIntLen
	if streamFrameIterations > 100:
		return (
			data,			# a byte array whose length should be the (frame_count * channels * bytes-per-channel) if output=True or None if output=False.
			pyaudio.paAbort	# must be either paContinue, paComplete or paAbort (one of PortAudio Callback Return Code). When output=True and out_data does not contain at least frame_count frames, paComplete is assumed for flag.
		)
	streamFrameIterations += 1
	return (
		data,				# a byte array whose length should be the (frame_count * channels * bytes-per-channel) if output=True or None if output=False.
		pyaudio.paContinue	# must be either paContinue, paComplete or paAbort (one of PortAudio Callback Return Code). When output=True and out_data does not contain at least frame_count frames, paComplete is assumed for flag.
	)

framesPerBuffer = 1024 * 1
# Returns a PortAudio format constant for the specified width.
format = pyAudioInstance.get_format_from_width(
	width = waveFile.getsampwidth() # The desired sample width in bytes (1, 2, 3, or 4)
)
channels = waveFile.getnchannels()
rate = waveFile.getframerate() # frequency

print("framesPerBuffer %s" % framesPerBuffer)
print("format %s" % format)
print("channels %s" % channels)
print("rate %s" % rate)

# Open a new stream. See constructor for Stream.__init__() for parameter details.
# Returns:	A new Stream
pyAudioStream = pyAudioInstance.open(
	# PA_manager,							# A reference to the managing PyAudio instance
	rate=rate,								# Sampling rate
	channels=channels,						# Number of channels
	format=format,							# Sampling size and format
	# input=True,							# Specifies whether this is an input stream. Defaults to False.
	output=True,							# Specifies whether this is an output stream. Defaults to False.
	# input_device_index=False,				# Index of Input Device to use. Unspecified (or None) uses default device. Ignored if input is False.
	# output_device_index=False,			# Index of Output Device to use. Unspecified (or None) uses the default device. Ignored if output is False.
	frames_per_buffer=framesPerBuffer,				# Specifies the number of frames per buffer.
	start=True,								# Start the stream running immediately. Defaults to True. In general, there is no reason to set this to False.
	# input_host_api_specific_stream_info,	# Specifies a host API specific stream information data structure for input.
	# output_host_api_specific_stream_info,	# Specifies a host API specific stream information data structure for output.
	stream_callback=pyAudioStreamCallback	# Specifies a callback function for non-blocking (callback) operation. Default is None, which indicates blocking operation (i.e., Stream.read() and Stream.write()).
	# Note: stream_callback is called in a separate thread (from the main thread). Exceptions that occur in the stream_callback will:
		# 1 print a traceback on standard error to aid debugging,
		# 2 queue the exception to be thrown (at some point) in the main thread, and
		# 3 return paAbort to PortAudio to stop the stream.
)

# Start the stream.
# pyAudioStream.start_stream() # this is started in pyAudioInstance.open()

plt.show()

# Returns whether the stream is active.
# Return type:	bool
while pyAudioStream.is_active():
	time.sleep(0.1)

# Stop the stream. Once the stream is stopped, one may not call write or read. Call start_stream() to resume the stream.
pyAudioStream.stop_stream()
# Close the stream
pyAudioStream.close()
waveFile.close()

# Terminate PortAudio
pyAudioInstance.terminate()