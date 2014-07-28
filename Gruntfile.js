module.exports = function(grunt) {
	var dependencies = [
		'bower_components/jquery/dist/jquery.js',
		'bower_components/jquery-cookie/jquery.cookie.js',
		'bower_components/bootstrap/dist/js/bootstrap.js',
		'bower_components/underscore/underscore.js',
		];
	grunt.initConfig({
		pkg: grunt.file.readJSON('package.json'),
		concat: {
			js: {
				src: dependencies,
				dest: 'static/js/lib.js'
			}
		},
		uglify : {
			options: {
				banner: '/*! <%= pkg.name %> - v<%= pkg.version %> - ' +
					'<%= grunt.template.today("yyyy-mm-dd") %> */',
			},
			js : {
				files : {
					"static/js/lib.min.js" : dependencies
				}
			}
		}
	});
	grunt.loadNpmTasks('grunt-contrib-concat');
	grunt.loadNpmTasks('grunt-contrib-uglify');
};
