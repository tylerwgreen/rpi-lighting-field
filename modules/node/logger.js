var winston = require('winston');

var logger = {
	init: function(params){
		winston.remove(winston.transports.Console);
		if(false !== params.config.console)
			winston.add(winston.transports.Console, {
				level: params.config.console
			});
		Object.keys(params.config.file).forEach(function(fileName){
			var logLevel = params.config.file[fileName];
			var file = params.logDir + params.config.fileDir + fileName + params.config.fileExt;
			winston.add(winston.transports.File, {
				name: fileName,
				filename: file,
				level: logLevel
			});
		});
		return winston;
	}
}
module.exports = logger;