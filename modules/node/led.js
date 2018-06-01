'use strict';

var Gpio = require('pigpio').Gpio;

class led{
	constructor(gpioPin){
		
		var self = this;
		this.interval = 1000; // milliseconds
		this.dutyCycleMax = 255;
		// make dutyCycleMax 256 before division, divide number should be divisible by 8
		this.dutyCycleStep = Math.round((this.dutyCycleMax + 1) / 24);
// console.log('dutyCycleStep', this.dutyCycleStep);
		this.gpioPin = gpioPin;
		this.led = new Gpio(this.gpioPin, {mode: Gpio.OUTPUT});
		
		this.destruct = function(){
			this.off();
		}
		
		this.on = function(){
			this.led.digitalWrite(1);
		}
		
		this.off = function(){
			this.led.digitalWrite(0);
		}
		
		this.blink = function(interval){
			this._setIntervalBlink(interval);
			this.on();
			var on = true;
// console.time('blinkTimer');
			var interval = setInterval(function(){
				if(on){
// console.log('blinkOff');
					self.off();
					// on = false;
					clearInterval(interval);
				}else{
// console.log('blinkOn');
					self.on();
					on = true;
// console.timeEnd('blinkTimer');
// console.time('blinkTimer');
				}
				
			}, this.interval);
		}
		
		this.breathe = function(interval){
		}
		
		this.fadeIn = function(interval){
			this._setIntervalDutyCycle(interval);
			this.off();
			var dutyCycle = 0;
// console.time('fadeInTimer');
			var interval = setInterval(function(){
// console.log('dutyCycle', dutyCycle);
				self.led.pwmWrite(dutyCycle);
				if(dutyCycle == self.dutyCycleMax){
					// dutyCycle = 0;
					self.off();
					clearInterval(interval);
// console.timeEnd('fadeInTimer');
// console.time('fadeInTimer');
				}else{
					dutyCycle += self.dutyCycleStep;
					if(dutyCycle > self.dutyCycleMax)
						dutyCycle = self.dutyCycleMax;
				}
			}, this.interval);
		}
		
		this.fadeOut = function(interval){
			this._setIntervalDutyCycle(interval);
			this.on();
			var dutyCycle = this.dutyCycleMax;
// console.time('fadeOutTimer');
			var interval = setInterval(function(){
// console.log('dutyCycle', dutyCycle);
				self.led.pwmWrite(dutyCycle);
				if(dutyCycle == 0){
					// dutyCycle = self.dutyCycleMax;
					self.off();
					clearInterval(interval);
// console.timeEnd('fadeOutTimer');
// console.time('fadeOutTimer');
				}else{
					dutyCycle -= self.dutyCycleStep;
					if(dutyCycle < 0)
						dutyCycle = 0;
				}
			}, this.interval);
		}
		
		this._setIntervalDutyCycle = function(interval){
			// make dutyCycleMax 256 before division, add one to account for loop reset
			var dutyCycleSteps = ((this.dutyCycleMax + 1) / this.dutyCycleStep) + 1;
// console.log('dutyCycleSteps', dutyCycleSteps);
			var interval = Math.round(interval / dutyCycleSteps);
			this._setInterval(interval);
		}
		
		this._setIntervalBlink = function(interval){
			interval = Math.round(interval / 2);
			this._setInterval(interval);
		}
		
		this._setInterval = function(interval){
			this.interval = interval;
// console.log('interval', this.interval);
		}

	}
}
module.exports = led;