const gulp = require('gulp');
const sass = require('gulp-sass')(require('sass'));
const concat = require('gulp-concat');
const uglify = require('gulp-uglify');
const cleanCSS = require('gulp-clean-css');
const autoprefixer = require('gulp-autoprefixer');
const imagemin = require('gulp-imagemin');
const plumber = require('gulp-plumber');
const notify = require('gulp-notify');
const browserSync = require('browser-sync').create();
const del = require('del');

// Шляхи
const paths = {
  scss: {
    src: 'static/src/scss/main.scss', 
    watch: 'static/src/scss/**/*.scss',
    dest: 'static/dist/css/'
  },
  js: {
    src: 'static/src/js/**/*.js',
    dest: 'static/dist/js/'
  },
  images: {
    src: 'static/src/img/**/*',
    dest: 'static/dist/img/'
  },
  fonts: {
    src: 'static/src/fonts/**/*',
    dest: 'static/dist/fonts/'
  }
};

// Очистка папки dist
function clean() {
  return del(['static/dist/**', '!static/dist']);
}

// Компіляція SCSS (dev з sourcemaps)
function styles() {
  return gulp
    .src(paths.scss.src, { sourcemaps: true })
    .pipe(plumber({
      errorHandler: notify.onError("Error: <%= error.message %>")
    }))
    .pipe(sass({
      outputStyle: 'expanded',
      includePaths: ['node_modules', 'static/src/scss']
    }).on('error', sass.logError))
    .pipe(autoprefixer({ cascade: false }))
    .pipe(gulp.dest(paths.scss.dest, { sourcemaps: '.' }))
    .pipe(browserSync.stream());
}

// Компіляція SCSS для продакшну
function stylesProd() {
  return gulp
    .src(paths.scss.src)
    .pipe(plumber({
      errorHandler: notify.onError("Error: <%= error.message %>")
    }))
    .pipe(sass({
      outputStyle: 'compressed',
      includePaths: ['node_modules', 'static/src/scss']
    }).on('error', sass.logError))
    .pipe(autoprefixer({ cascade: false }))
    .pipe(cleanCSS({ level: 2 }))
    .pipe(gulp.dest(paths.scss.dest));
}

// Обробка JavaScript (dev з sourcemaps)
function scripts() {
  return gulp
    .src(paths.js.src, { sourcemaps: true })
    .pipe(plumber({
      errorHandler: notify.onError("Error: <%= error.message %>")
    }))
    .pipe(gulp.dest(paths.js.dest, { sourcemaps: '.' }))
    .pipe(browserSync.stream());
}

// Обробка JavaScript для продакшну
function scriptsProd() {
  return gulp
    .src(paths.js.src)
    .pipe(plumber({
      errorHandler: notify.onError("Error: <%= error.message %>")
    }))
    .pipe(uglify())
    .pipe(gulp.dest(paths.js.dest));
}

// Оптимізація зображень
function images() {
  return gulp
    .src(paths.images.src)
    .pipe(imagemin([
      imagemin.gifsicle({ interlaced: true }),
      imagemin.mozjpeg({ quality: 80, progressive: true }),
      imagemin.optipng({ optimizationLevel: 5 }),
      imagemin.svgo({
        plugins: [
          { removeViewBox: true },
          { cleanupIDs: false }
        ]
      })
    ]))
    .pipe(gulp.dest(paths.images.dest));
}

// Копіювання шрифтів
function fonts() {
  return gulp
    .src(paths.fonts.src)
    .pipe(gulp.dest(paths.fonts.dest));
}

// BrowserSync
function serve() {
  browserSync.init({
    proxy: "localhost:8000", // Django dev server
    port: 3000,
    open: false,
    notify: false,
    files: ["static/dist/**/*"],
    watchEvents: ['change', 'add', 'unlink']
  });
}

// Відстеження змін
function watchFiles() {
  gulp.watch(paths.scss.watch, styles);
  gulp.watch(paths.js.src, scripts);
  gulp.watch(paths.images.src, images);
  gulp.watch("templates/**/*.html").on('change', browserSync.reload);
  gulp.watch("static/dist/css/*.css").on('change', browserSync.reload);
}

// Задачі
gulp.task('clean', clean);
gulp.task('styles', styles);
gulp.task('styles:prod', stylesProd);
gulp.task('scripts', scripts);
gulp.task('scripts:prod', scriptsProd);
gulp.task('images', images);
gulp.task('fonts', fonts);

// Основні команди
gulp.task('dev', gulp.series(clean, gulp.parallel(styles, scripts, images, fonts)));
gulp.task('build', gulp.series(clean, gulp.parallel(stylesProd, scriptsProd, images, fonts)));
gulp.task('watch', gulp.parallel(watchFiles, serve));

// Дефолтна задача
gulp.task('default', gulp.series('dev', 'watch'));
