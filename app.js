// var pigpio = require('pigpio');
var led = require(__dirname + '/modules/node/led');
var logger = require(__dirname + '/modules/node/logger');
var pythonInterface = require(__dirname + '/modules/node/python-interface');

var app = {
	init: function(){
		console.log('app.init()');
		this.config = require('config');
		this.logger = logger.init({
			config: this.config.get('logger'),
			logDir: __dirname
		});
		/* var interval = 1000;
		for(var i = 1; i <= 20; i++){
			// console.log(i);
			var led1 = new led(i + 1);
			// led.blink(interval);
			// led.fadeOut(interval);
			led1.fadeIn(interval);
			interval -= Math.round(interval / 20);
		} */
		// led1.fadeOut(250);
		this.pythonInterface = pythonInterface.init({
			config:		this.config.get('pythonInterface'),
			logger:		this.logger,
			ledLo:		new led(2),
			ledMid:		new led(10),
			ledHi:		new led(20),
			scriptPath:	__dirname + '/modules/python/',
			script:		'App.py'
		});
		this._registerpythonInterfaceCommands();
		// this.pythonInterface.testTest()
// return;
		// return;
		// WAVE FILES
		// var waveFile = '0_16.wav' # single freq
		// var waveFile = 'tone.wav' # freq sweep
		// var waveFile = 'technologic.wav'
		// var waveFile = 'technologic-real.wav'
		// var waveFile = 'cello.wav'
		// var waveFile = 'getaway-16-44.wav'
		// var waveFile = 'getaway-16-48.wav'
		// var waveFile = 'drums-01.wav'
		// var waveFile = '1k-octaves.wav'
		var waveFile = '440-octaves.wav'
		// var waveFile = '440-stereo.wav' # 440 khz tone
		// var waveFile = '440-mono.wav' # 440 khz tone
		// var waveFile = '440-stereo-loud.wav'
		// var waveFile = '440-mono-loud.wav'
		// var waveFile = '440-mono-half-as-loud.wav' # 440 khz tone half as loud as 440-mono.wav
		// var waveFile = '440-mono-quiet.wav' # 440 khz tone quieter than 440-mono.wav
		// var waveFile = '440-mono-16-44-0db.wav' # 440 khz tone
		this.playAudioFile(waveFile);
	},
	_registerpythonInterfaceCommands: function(){
		console.log('app._registerpythonInterfaceCommands()');
		app.pythonInterface.registerCommand('message', app._message);
		app.pythonInterface.registerCommand('audioPeaks', app._audioPeaks);
		app.pythonInterface.registerCommand('audioComplete', app._audioComplete);
	},
	_message: function(data){
		console.log('app._message()', data.content);
	},
	_audioPeaks: function(data){
		console.log('app._audioPeaks()', data);
		if(typeof data.data[0] === 'undefined')
			throw new Error('Missing or illegal data attributes: ' + data);
		if(typeof data.data[0] !== 'undefined'){
			/*
			0,	# [20, 40]
			1,	# [40, 80]
			2,	# [80, 160]
			3,	# [160, 320]
			4,	# [320, 640]
			5,	# [640, 1280]
			6,	# [1280, 2560]
			7,	# [2560, 5120]
			8,	# [5120, 10240]
			9	# [10240, 20000]
			
			Bass (Kick) Drum	60Hz - 100Hz	35 - 115
			Snare Drum	120 Hz - 250 Hz	
			Cymbal - Hi-hat	3 kHz - 5 kHz	4 - 110
			*/
			// var peakLo = data.data[0] + data.data[1]  + data.data[2];
			var peakLo = data.data[0] + data.data[1];
			// var peakMid = data.data[4] + data.data[5] + data.data[6];
			// var peakMid = data.data[2] + data.data[3];
			var peakMid = data.data[3] + data.data[4];
			var peakHi = data.data[8] + data.data[9];
			var peakLoTop = 5500;
			var peakMidTop = 1300;
			var peakHiTop = 30;
			// if(peakLo >= peakLoTop - 500) console.log(peakLo);
			// if(peakMid >= peakMidTop - 150) console.log(peakMid);
			if(peakHi >= peakHiTop - 15) console.log(peakHi);
			if(peakLo >= peakLoTop){
				// console.log('peakLo: ' + peakLo);
				pythonInterface.ledLo.fadeOut(100);
			}
			if(peakMid >= peakMidTop){
				// console.log('peakMid: ' + peakMid);
				pythonInterface.ledMid.fadeOut(100);
			}
			if(peakHi >= peakHiTop){
				// console.log('peakHi: ' + peakHi);
				pythonInterface.ledHi.fadeOut(50);
			}
		}
	},
	_audioComplete: function(data){
		console.log('app._audioComplete()', data);
		app.playAudioFile('1k-octaves.wav');
	},
	playAudioFile: function(audioFile){
		console.log('app.playAudioFile()', audioFile);
		app.pythonInterface.sendCommand('play', {
			'file': __dirname + '/assets/audio/' + audioFile
		});
	}
}
app.init();