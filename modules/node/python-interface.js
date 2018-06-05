var pyShell = require('python-shell');

var pythonInterface = {
	commands: {},
	init: function(params){
		this.config = params.config;
		this.logger = params.logger;
		this.ledLo = params.ledLo;
		this.ledMid = params.ledMid;
		this.ledHi = params.ledHi;
		// this.logger.info('pythonInterface.init', params);
		this.pyShell = new pyShell(params.script, {
			mode:		'json',
			scriptPath:	params.scriptPath
		});
		this._configureListeners();
		return this;
	},
	_configureListeners: function(){
		// this.logger.info('pythonInterface._configureListeners');
		this.pyShell.on('message', this._pyShellMessage);
		this.pyShell.on('error', this._pyShellError);
		this.pyShell.on('close', this._pyShellClose);
	},
	_pyShellMessage: function(json){
		// pythonInterface.logger.info('pythonInterface._pyShellMessage');
		if(json){
			if(json.data){
				pythonInterface.logger.debug('pythonInterface._pyShellMessage');
				if(json.data.isArray){
					var data = json.data[0];
				}else{
					var data = json.data;
				}
				if(data.type === 'audioPeaks'){
					if(typeof data.attributes.data[0] !== 'undefined'){
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
						// var peakLo = data.attributes.data[0] + data.attributes.data[1]  + data.attributes.data[2];
						var peakLo = data.attributes.data[0] + data.attributes.data[1];
						// var peakMid = data.attributes.data[4] + data.attributes.data[5] + data.attributes.data[6];
						// var peakMid = data.attributes.data[2] + data.attributes.data[3];
						var peakMid = data.attributes.data[3] + data.attributes.data[4];
						var peakHi = data.attributes.data[8] + data.attributes.data[9];
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
				}else{
					console.log(data);
				}
				// pythonInterface.logger.debug(data.attributes.result);
			}else if(json.errors){
				pythonInterface._handlJsonErrors(json.errors);
			}else{
				pythonInterface.logger.error('pythonInterface._pyShellMessage|Json does not contain data or errors');
			}
		}else{
		}
	},
	_pyShellClose: function(){
		// pythonInterface.logger.info('pythonInterface._pyShellClose');
	},
	_pyShellError: function(error){
		// pythonInterface.logger.info('pythonInterface._pyShellError');
		if(error)
			pythonInterface.logger.error('pythonInterface._pyShellError|' + error.message);
	},
	_handlJsonErrors: function(errors){
		// pythonInterface.logger.info('pythonInterface._handlJsonErrors');
		Object.keys(errors).forEach(function(key) {
			var val = errors[key];
			pythonInterface.logger.error('pythonInterface._handlJsonErrors|Error ' + key + '|' + val.detail);
		});
		pythonInterface.pyShell.end(function(err, code, signal){
			if(err)
				throw err;
			pythonInterface.logger.error('pythonInterface._handlJsonErrors|The exit code was: ' + code);
			pythonInterface.logger.error('pythonInterface._handlJsonErrors|The exit signal was: ' + signal);
			pythonInterface.logger.error('pythonInterface._handlJsonErrors|finished');
		});
		pythonInterface.pyShell.terminate();
	},
	sendCommand: function(command, attributes){
		if(typeof attributes === 'undefined')
			attributes = {};
		pythonInterface.pyShell.send({
			data: {
				type: 'command',
				id: command,
				attributes: attributes
			}
		});
	},
	testTest: function(){
		// this.logger.info('pythonInterface.testTest');
		// console.log(this);
		this.logger.info('test');
		// this.pyShell.send({data:{type:'command',id:'getCommands'}});
		// this.pyShell.send({data:{type:'command',id:'play'}});
		// this.pyShell.send({data:{type:'command',id:'removePlay'}});
		// this.pyShell.send({data:{type:'command',id:'play'}});
		// this.pyShell.send({data:{type:'command',id:'getInterval'}});
		// this.pyShell.send({data:{type:'command',id:'stop'}});
		// this.pyShell.send({data:{type:'asdf',id:'asdf'}});
		// this.pyShell.send({command: 'illegal'});
		// pythonInterface.pyShell.send({data:{type:'command',id:'getInterval'}});
	}
}
module.exports = pythonInterface;