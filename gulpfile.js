var gulp = require('gulp');

gulp.task('sprite', function() {
	var spriteData = 
		gulp.src('img/sprite/*.*') // путь, откуда берем картинки для спрайта
			.pipe(spritesmith({
				imgName: 'sprite.png',
				cssName: 'sprite.sass',
				cssFormat: 'sass',
				algorithm: 'binary-tree',
				cssTemplate: 'sass.template.mustache',
				cssVarMap: function(sprite) {
					sprite.name = 's-' + sprite.name
				}
			}));

	spriteData.img.pipe(gulp.dest('img/')); // путь, куда сохраняем картинку
	spriteData.css.pipe(gulp.dest('sass/')); // путь, куда сохраняем стили
});