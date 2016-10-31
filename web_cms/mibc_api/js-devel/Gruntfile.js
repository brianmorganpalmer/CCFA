module.exports = function(grunt) {
    
    grunt.initConfig({
	pkg: grunt.file.readJSON("package.json"),

	coffee: {
	    compile: {
		options: {
		    bare: true
		},
		files: {
		    "../static/js/metadata.js": [ 
			"mibc/js/MIBC.coffee"
			, "mibc/js/metadata.js.coffee"
			]
		    , "../static/js/validator.js": [ 
			"mibc/js/MIBC.coffee" 
			, "mibc/js/validator.js.coffee"
			]
		    , "../static/js/samplemeta.js": [ 
			"mibc/js/MIBC.coffee" 
			, "mibc/js/samplemeta.js.coffee"
			]
		},
	    },
	},

	shell: {
	    bower: {
		options: {
		    stdout: true
		},
		command: "./node_modules/bower/bin/bower install"
	    },
	},

    });

    grunt.loadNpmTasks("grunt-contrib-coffee");
    grunt.loadNpmTasks("grunt-shell");

    grunt.registerTask("default", ["coffee", "shell"]);
    grunt.registerTask("dev", ["coffee"]);
    grunt.registerTask("clean", ["clean"]);

};