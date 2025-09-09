// gulpfile.js
import gulp from "gulp";
import gulpSass from "gulp-sass";
import * as dartSass from "sass";
import concat from "gulp-concat";
import uglify from "gulp-uglify";
import cleanCSS from "gulp-clean-css";
import autoprefixer from "gulp-autoprefixer";
import plumber from "gulp-plumber";
import notify from "gulp-notify";
import browserSyncLib from "browser-sync";
import { deleteAsync } from "del";

const sass = gulpSass(dartSass);
const browserSync = browserSyncLib.create();

// Шляхи
const paths = {
  scss: {
    src: "static/src/scss/main.scss",
    watch: "static/src/scss/**/*.scss",
    dest: "static/dist/css/",
  },
  js: {
    src: "static/src/js/**/*.js",
    dest: "static/dist/js/",
  },
  images: {
    src: "static/src/img/**/*",
    dest: "static/dist/img/",
  },
  fonts: {
    src: "static/src/fonts/**/*",
    dest: "static/dist/fonts/",
  },
};

// Очистка
export function clean() {
  return deleteAsync(["static/dist/**", "!static/dist"]);
}

// SCSS (dev з sourcemaps)
export function styles() {
  return gulp
    .src(paths.scss.src, { sourcemaps: true })
    .pipe(
      plumber({
        errorHandler: notify.onError("Error: <%= error.message %>"),
      })
    )
    .pipe(
      sass({
        outputStyle: "expanded",
        includePaths: ["node_modules", "static/src/scss"],
      }).on("error", sass.logError)
    )
    .pipe(autoprefixer({ cascade: false }))
    .pipe(gulp.dest(paths.scss.dest, { sourcemaps: "." }))
    .pipe(browserSync.stream());
}

// SCSS (prod)
export function stylesProd() {
  return gulp
    .src(paths.scss.src)
    .pipe(
      plumber({
        errorHandler: notify.onError("Error: <%= error.message %>"),
      })
    )
    .pipe(
      sass({
        outputStyle: "compressed",
        includePaths: ["node_modules", "static/src/scss"],
      }).on("error", sass.logError)
    )
    .pipe(autoprefixer({ cascade: false }))
    .pipe(cleanCSS({ level: 2 }))
    .pipe(gulp.dest(paths.scss.dest));
}

// JS (dev)
export function scripts() {
  return gulp
    .src(paths.js.src, { sourcemaps: true })
    .pipe(
      plumber({
        errorHandler: notify.onError("Error: <%= error.message %>"),
      })
    )
    .pipe(gulp.dest(paths.js.dest, { sourcemaps: "." }))
    .pipe(browserSync.stream());
}

// JS (prod)
export function scriptsProd() {
  return gulp
    .src(paths.js.src)
    .pipe(
      plumber({
        errorHandler: notify.onError("Error: <%= error.message %>"),
      })
    )
    .pipe(uglify())
    .pipe(gulp.dest(paths.js.dest));
}

// Images з оптимізацією
export async function images() {
  try {
    const imagemin = (await import("gulp-imagemin")).default;
    const imageminGifsicle = (await import("imagemin-gifsicle")).default;
    const imageminMozjpeg = (await import("imagemin-mozjpeg")).default;
    const imageminOptipng = (await import("imagemin-optipng")).default;
    const imageminSvgo = (await import("imagemin-svgo")).default;
    
    return gulp
      .src(paths.images.src)
      .pipe(
        imagemin([
          imageminGifsicle({ interlaced: true }),
          imageminMozjpeg({ quality: 80, progressive: true }),
          imageminOptipng({ optimizationLevel: 5 }),
          imageminSvgo({
            plugins: [
              { 
                name: 'preset-default',
                params: {
                  overrides: {
                    removeViewBox: false,
                    cleanupIds: false
                  }
                }
              }
            ],
          }),
        ])
      )
      .pipe(gulp.dest(paths.images.dest));
  } catch (error) {
    console.log("ImageMin plugins not found. Installing imagemin plugins...");
    console.log("Run: npm install --save-dev imagemin-gifsicle imagemin-mozjpeg imagemin-optipng imagemin-svgo");
    // Fallback - просто копіюємо зображення без оптимізації
    return gulp.src(paths.images.src).pipe(gulp.dest(paths.images.dest));
  }
}

// Fonts
export function fonts() {
  return gulp.src(paths.fonts.src).pipe(gulp.dest(paths.fonts.dest));
}

// BrowserSync
export function serve() {
  browserSync.init({
    proxy: "localhost:8000", // Django dev server
    port: 3000,
    open: false,
    notify: false,
    files: ["static/dist/**/*"],
    watchEvents: ["change", "add", "unlink"],
  });
}

// Watch
export function watchFiles() {
  gulp.watch(paths.scss.watch, styles);
  gulp.watch(paths.js.src, scripts);
  gulp.watch(paths.images.src, images);
  gulp.watch("templates/**/*.html").on("change", browserSync.reload);
  gulp.watch("static/dist/css/*.css").on("change", browserSync.reload);
}

// Груповані задачі
export const dev = gulp.series(clean, gulp.parallel(styles, scripts, images, fonts));
export const build = gulp.series(clean, gulp.parallel(stylesProd, scriptsProd, images, fonts));
export const watch = gulp.parallel(watchFiles, serve);

// За замовчуванням
export default gulp.series(dev, watch);