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

		sprite:{
			all: {
				src: 'static/img/sprite_dashboard/*.*',
				destImg: 'static/img/sprite_sheet.png',
				destCSS:  'templates/dashboard/sass/_sprites.sass',
				algorithm: 'binary-tree',
				padding: 2,
				cssVarMap: function(sprite) {
					sprite.name = 's-' + sprite.name
				},
			},
		},
	});

	require('load-grunt-tasks')(grunt);
	grunt.registerTask('default', ['sprite']);
};