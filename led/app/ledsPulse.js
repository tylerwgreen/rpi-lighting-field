var raspiIO = require('raspi-io');
var five = require('johnny-five');
var Gpio = require('pigpio').Gpio;


var ledsPulse = {
	_debug: true,
	_settings: {
		/* seconds_between_readings: null,
		readings_ranges: {
			temperature: {
				hi: null,
				lo: null
			},
			humidity: {
				hi: null,
				lo: null
			},
			water_level: {
				hi: null,
				lo: null
			}
		} */
	},
	init: function(gpioPins){
		// return led.testA();
		return led.testB();
	},
	testA: function(){
		return new Promise((resolve, reject) => {
			var board = new five.Board({
				io: new raspiIO()
			});
			board.on('ready', function(){
				// var ledBlue1 = new five.Led('GPIO5');
				// var ledRed = new five.Led('GPIO6');
				// var ledGreen = new five.Led('GPIO13');
				// var ledYellow = new five.Led('GPIO12');
				// var ledBlue2 = new five.Led('GPIO26');
				// ledBlue1.blink(100);
				// ledRed.blink(200);
				// ledGreen.blink(300);
				// ledYellow.blink(400);
				// ledBlue2.blink(500);
				var ledsOne = new five.Leds([
					'GPIO18',
					// 'GPIO12',
					'GPIO13',
					// 'GPIO19',
					// 'GPIO26',
				]);
				var ledsTwo = new five.Leds([
					// 'GPIO18',
					'GPIO16',
					// 'GPIO13',
					'GPIO6',
					'GPIO26',
				]);
				// var testPin = new five.Pin({
					// id: 'test',
					// pin: 'GPIO16',
					// type: 'analog',
					// mode: 3
				// });
				// testPin.pulse();
				ledsOne.pulse();
				ledsTwo.blink();
				resolve('led blink success');
			});
			// reject(err);
		});
	},
	testB: function(){
		return new Promise((resolve, reject) => {
			led1 = new Gpio(2, {mode: Gpio.OUTPUT}),
			led2 = new Gpio(3, {mode: Gpio.OUTPUT}),
			led3 = new Gpio(4, {mode: Gpio.OUTPUT}),
			led4 = new Gpio(5, {mode: Gpio.OUTPUT}),
			led5 = new Gpio(6, {mode: Gpio.OUTPUT}),
			led6 = new Gpio(7, {mode: Gpio.OUTPUT}),
			led7 = new Gpio(8, {mode: Gpio.OUTPUT}),
			led8 = new Gpio(9, {mode: Gpio.OUTPUT}),
			led9 = new Gpio(10, {mode: Gpio.OUTPUT}),
			led10 = new Gpio(11, {mode: Gpio.OUTPUT}),
			led11 = new Gpio(12, {mode: Gpio.OUTPUT}),
			led12 = new Gpio(13, {mode: Gpio.OUTPUT}),
			led13 = new Gpio(14, {mode: Gpio.OUTPUT}),
			led14 = new Gpio(15, {mode: Gpio.OUTPUT}),
			led15 = new Gpio(16, {mode: Gpio.OUTPUT}),
			led16 = new Gpio(17, {mode: Gpio.OUTPUT}),
			led17 = new Gpio(18, {mode: Gpio.OUTPUT}),
			led18 = new Gpio(19, {mode: Gpio.OUTPUT}),
			led19 = new Gpio(20, {mode: Gpio.OUTPUT}),
			led20 = new Gpio(21, {mode: Gpio.OUTPUT}),
			dutyCycle = 0;
			setInterval(function(){
				led1.pwmWrite(dutyCycle);
				led2.pwmWrite(dutyCycle);
				led3.pwmWrite(dutyCycle);
				led4.pwmWrite(dutyCycle);
				led5.pwmWrite(dutyCycle);
				led6.pwmWrite(dutyCycle);
				led7.pwmWrite(dutyCycle);
				led8.pwmWrite(dutyCycle);
				led9.pwmWrite(dutyCycle);
				led10.pwmWrite(dutyCycle);
				led11.pwmWrite(dutyCycle);
				led12.pwmWrite(dutyCycle);
				led13.pwmWrite(dutyCycle);
				led14.pwmWrite(dutyCycle);
				led15.pwmWrite(dutyCycle);
				led16.pwmWrite(dutyCycle);
				led17.pwmWrite(dutyCycle);
				led18.pwmWrite(dutyCycle);
				led19.pwmWrite(dutyCycle);
				led20.pwmWrite(dutyCycle);
				dutyCycle += 5;
				if(dutyCycle > 255){
					dutyCycle = 0;
			}}, 20);
			// reject(err);
		});
	},
	/* update: function(newSettings){
		settings._log('update', newSettings);
		settings._settings = newSettings;
	},
	getSecondsBetweenReadings: function(){
		settings._log('getSecondsBetweenReadings', settings._settings.seconds_between_readings);
		return settings._settings.seconds_between_readings;
	},
	getMillisecondsBetweenReadings: function(){
		settings._log('getMillisecondsBetweenReadings', settings._settings.seconds_between_readings);
		return settings._settings.seconds_between_readings * 1000;
	},
	getReadingsRanges: function(){
		settings._log('getReadingsRanges', settings._settings.readings_ranges);
		return settings._settings.readings_ranges;
	},
	validateReading: function(reading){
		settings._log('validateReading', reading);
		return new Promise((resolve, reject) => {
			settings._validateTemperatureReading(reading.temperature)
			.then(settings._validateHumidityReading(reading.humidity))
			.then(settings._validateWaterLevelReading(reading.water_level))
			.then(function(){
				resolve('validateReading|Valid');
			})
			.catch(function(err){
				reject(err);
			});
		});
	},
	_validateTemperatureReading: function(reading){
		settings._log('validateTemperatureReading', reading);
		return new Promise((resolve, reject) => {
			if(reading > settings._settings.readings_ranges.temperature.hi)
				reject('validateTemperatureReading|Invalid|Too Hi|' + reading);
			else if(reading < settings._settings.readings_ranges.temperature.lo)
				reject('validateTemperatureReading|Invalid|Too Low|' + reading);
			resolve('validateTemperatureReading|Valid');
		});
	},
	_validateHumidityReading: function(reading){
		settings._log('validateHumidityReading', reading);
		return new Promise((resolve, reject) => {
			if(reading > settings._settings.readings_ranges.humidity.hi)
				reject('validateHumidityReading|Invalid|Too Hi|' + reading);
			else if(reading < settings._settings.readings_ranges.humidity.lo)
				reject('validateHumidityReading|Invalid|Too Low|' + reading);
			resolve('validateHumidityReading|Valid');
		});
	},
	_validateWaterLevelReading: function(reading){
		settings._log('validateWaterLevelReading', reading);
		return new Promise((resolve, reject) => {
			if(reading > settings._settings.readings_ranges.water_level.hi)
				reject('validateWaterLevelReading|Invalid|Too Hi|' + reading);
			else if(reading < settings._settings.readings_ranges.water_level.lo)
				reject('validateWaterLevelReading|Invalid|Too Low|' + reading);
			resolve('validateWaterLevelReading|Valid');
		});
	}, */
	_log: function(msg){
		if(settings._debug)
			console.log('settings.' + msg);
	}
}
module.exports = ledsPulse;