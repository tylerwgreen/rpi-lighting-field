var winston = require('winston');
var config = require('config');
var pigpio = require('pigpio');
var Led = require(__dirname + '/app/Led');

var app = {
	init: function(){
		app.config = config;
		app.logger = winston;
		app.console.logLevel = config.get('console.logLevel');
		console.log(app.console.logLevel);
		app.logger.add(winston.transports.File, {filename: __dirname + config.get('logger.logFile')});
		app.console.debug('app.init|success');
		// app.led = require(__dirname + '/app/led');
		// app.led = require(__dirname + '/app/ledsPulse');
		process.on('SIGINT', function() {
			console.log("Caught interrupt signal");
			led.destruct();
			pigpio.terminate(); // pigpio C library terminated here
		});
		var leds = [];
		var interval = 1000;
		for(var i = 1; i <= 20; i++){
			// console.log(i);
			var led = new Led(i + 1);
			// led.blink(interval);
			// led.fadeOut(interval);
			led.fadeIn(interval);
			interval -= Math.round(interval / 20);
		}
		// array.forEach(function(item) {})
		// console.log(leds);
		// var led = new Led(2);
		// led.fadeIn(1000);
		// led.fadeOut(1000);
		// led.blink(1000);
		// led.on();
		// led.off();
		/* app.led.init()
			.then(function(settings){
				app.console.info('app.led.init success');
				// app.led.blink();
			})
			.catch(function(error){
				throw new Error('Could not initialize led|' + error);
			}); */
	},
	error: function(error){
		app.console.debug('app.error', error);
		if(error.message)
			error = error.message;
		app.console.error(error);
		app.logger.error(error);
	},
	console: {
		logLevel: null,
		getLogLevelNumber: function(logLevelName){
			if(logLevelName === 'debug')
				return 0;
			else if(logLevelName === 'info')
				return 1;
			else if(logLevelName === 'error')
				return 2;
			else
				throw new Error('Illegal logLevelName: ', logLevelName);
		},
		canLog: function(logLevelName){
			return app.console.getLogLevelNumber(logLevelName) >= app.console.getLogLevelNumber(app.console.logLevel) ? true : false;
		},
		debug: function(msg, params){
			if(!app.console.canLog('debug'))
				return;
			var params = typeof params === 'undefined' ? {} : params;
			console.log('DEBUG|' + msg, params);
		},
		info: function(msg, params){
			if(!app.console.canLog('info'))
				return;
			var params = typeof params === 'undefined' ? {} : params;
			console.log('INFO|' + msg, params);
		},
		error: function(msg, params){
			if(!app.console.canLog('error'))
				return;
			var params = typeof params === 'undefined' ? {} : params;
			console.log('ERROR|' + msg, params);
		}
	}
}
app.init();