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
	registerCommand: function(commandId, command){
		this.commands[commandId] = command
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
				// pythonInterface.logger.debug('pythonInterface._pyShellMessage');
				if(json.data.isArray)
					var data = json.data[0];
				else
					var data = json.data;
				if(pythonInterface.commands.hasOwnProperty(data.type))
					pythonInterface.commands[data.type](data.attributes);
				else
					throw new Error('Undefined data.type: ' + data.type);
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