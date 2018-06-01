// var pigpio = require('pigpio');
var led = require(__dirname + '/modules/node/led');
var logger = require(__dirname + '/modules/node/logger');
var pythonInterface = require(__dirname + '/modules/node/python-interface');

var app = {
	init: function(){
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
			config: this.config.get('pythonInterface'),
			logger: this.logger,
			ledLo: new led(2),
			ledMid: new led(10),
			ledHi: new led(20),
			appFile: 'modules/python/App.py'
		});
		// this.pythonInterface.testTest()
		// return;
		// WAVE FILES
		// var waveFile = '0_16.wav' # single freq
		// var waveFile = 'tone.wav' # freq sweep
		// var waveFile = 'technologic.wav'
		// var waveFile = 'technologic-real.wav'
		var waveFile = 'getaway-16-44.wav'
		// var waveFile = 'getaway-16-48.wav'
		// var waveFile = 'drums-01.wav'
		// var waveFile = '1k-octaves.wav'
		// var waveFile = '440-octaves.wav'
		// var waveFile = '440-stereo.wav' # 440 khz tone
		// var waveFile = '440-mono.wav' # 440 khz tone
		// var waveFile = '440-stereo-loud.wav'
		// var waveFile = '440-mono-loud.wav'
		// var waveFile = '440-mono-half-as-loud.wav' # 440 khz tone half as loud as 440-mono.wav
		// var waveFile = '440-mono-quiet.wav' # 440 khz tone quieter than 440-mono.wav
		// var waveFile = '440-mono-16-44-0db.wav' # 440 khz tone
		this.pythonInterface.sendCommand('play', {
			'file': waveFile
		});
	}
}
app.init();