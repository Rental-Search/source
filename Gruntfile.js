module.exports = function(grunt) {
	grunt.initConfig({
		pkg: grunt.file.readJSON('package.json'),
		banner: '/*\n * project name:      <%= pkg.name %>\n' +
						' * project developer: <%= pkg.developer %>, <%= pkg.company %>\n' +
						' * project versuon:   <%= pkg.version %>\n' +
						' * date created:      <%= grunt.template.today("yyyy-mm-dd") %> \n */\n\n',
		dirs: {
			prod: 'prod/<%= grunt.template.today("dd.mm.yyyy") %> - v(<%= pkg.version %>)',
			//min: 'prod.min/version.min(<%= grunt.template.today("yyyy-mm-dd") %>)',
		},

		jade: {
			compile: {
				files: [{
					cwd: 'dev/',
					src: ['**/*.jade'],
					dest: '<%= dirs.prod %>/',
					expand: true,
					ext: '.html',
				}],
			},
			options: {
				pretty: true,
			},
		},

		sass: {
			dist: {
				files: [{
					cwd: 'dev/sass',
					src: ['**/*.sass'],
					dest: 'css/',
					// expand: true,
					ext: '.css',
				}],
			},
		},

		jshint: {
			files: [ 'Gruntfile.js', 'dev/**/js/*.js' ],
		},

		concat: {
			options: {
				process: function(src, filepath) {
					return '/*\n' + ' * Source: '+ filepath + '\n */\n' + src;
				},
				banner: '<%= banner %>',
			},
			prod: {
				files: {
					'<%= dirs.prod %>/js/scripts.js': 'dev/js/*.js',
				},
			},
		},

		imagemin: {
			files: {
				expand: true,
				cwd: 'dev/img/',
				src: '**/*.{png,jpg,gif}',
				dest: '<%= dirs.prod %>/img/',
			},
		},

		watch: {
			livereload: {
				options: {
					livereload: true,
				},
				files: ['dev/**/*'],
			},
			jade: {
				files: ['<%= jade.compile.files[0].cwd %>/<%= jade.compile.files[0].src %>'],
				tasks: ['jade'],
				options: {
					spawn: false,
				},
			},
			js_hint: {
				files: ['<%= jshint.files %>'],
				tasks: ['jshint'],
				options: {
					spawn: false,
				},
			},
			js_concat: {
				files: ['<%= concat.prod.src %>'],
				tasks: ['concat'],
				options: {
					spawn: false,
				},
			},
			img: {
				files: ['dev/img/**/*.{png,jpg,gif}'],
				tasks: ['imagemin'],
				options: {
					spawn: false,
				},
			},
		},
		connect: {
			options: {
				port: 9000,
				hostname: 'localhost',
				livereload: 35729
			},
			livereload: {
				options: {
					open: true,
					base: ['./<%= dirs.prod %>']
				}
			}
		},
		sprite:{
			all: {
				src: 'img/sprite/*.*',
				destImg: 'img/spritesheet.png',
				destCSS: 'sass/sprites.sass',
				algorithm: 'binary-tree',
				cssVarMap: function(sprite) {
					sprite.name = 's-' + sprite.name
				},
			},
		},
	});

	require('load-grunt-tasks')(grunt);
	grunt.registerTask('default', ['connect:livereload','watch']);
	grunt.registerTask('compile', [
			'jade',
			'sass',
			'jshint',
			'concat',
			'imagemin',
		]);
	// grunt.registerTask('default', [
	// 	'concat',
	// 	'imagemin',
	// 	'jshint',
	// 	'jade',
	// 	]);
};