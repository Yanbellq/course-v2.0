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
import postcss from "gulp-postcss";
import sourcemaps from "gulp-sourcemaps";
import rename from "gulp-rename";
import imagemin, { gifsicle, mozjpeg, optipng, svgo } from "gulp-imagemin";

const sass = gulpSass(dartSass);
const browserSync = browserSyncLib.create();

// Шляхи
const paths = {
    scss: {
        src: "static/src/scss/crm/main.scss",
        watch: "static/src/scss/crm/**/*.scss",
        dest: "static/dist/css/crm/",
    },
    tailwind: {
        src: "static/src/css/tailwind.css",
        watch: ["static/src/css/**/*.css", "templates/**/*.html", "**/*.py"],
        dest: "static/dist/css/",
    },
    js: {
        src: "static/src/js/crm/**/*.js",
        dest: "static/dist/js/crm/",
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

// ========== ОЧИСТКА ==========
export function clean() {
    return deleteAsync(["static/dist/**", "!static/dist"]);
}

// ========== SASS КОМПІЛЯЦІЯ ==========
export function styles() {
    return gulp
        .src(paths.scss.src, { sourcemaps: true })
        .pipe(
            plumber({
                errorHandler: notify.onError({
                    title: "SCSS Error",
                    message: "<%= error.message %>",
                }),
            })
        )
        .pipe(
            sass({
                outputStyle: "expanded",
                includePaths: ["node_modules", "static/src/scss/crm"],
            }).on("error", sass.logError)
        )
        .pipe(
            autoprefixer({
                cascade: false,
            })
        )
        .pipe(gulp.dest(paths.scss.dest, { sourcemaps: "." }))
        .pipe(browserSync.stream());
}

// ========== TAILWIND CSS ОБРОБКА ==========
export function tailwind() {
    return gulp
        .src(paths.tailwind.src, { sourcemaps: true })
        .pipe(
            plumber({
                errorHandler: notify.onError({
                    title: "Tailwind Error",
                    message: "<%= error.message %>",
                }),
            })
        )
        .pipe(postcss())
        .pipe(rename("tailwind.css"))
        .pipe(gulp.dest(paths.tailwind.dest, { sourcemaps: "." }))
        .pipe(browserSync.stream());
}

// ========== МІНІМІЗАЦІЯ CSS (для продакшну) ==========
export function minifyStyles() {
    return gulp
        .src("static/dist/css/crm/**/*.css")
        .pipe(sourcemaps.init({ loadMaps: true }))
        .pipe(
            cleanCSS({
                level: 2,
                compatibility: "ie11",
            })
        )
        .pipe(
            rename({
                suffix: ".min",
            })
        )
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest(paths.scss.dest));
}

// ========== JAVASCRIPT ==========
export function scripts() {
    return gulp
        .src(paths.js.src, { sourcemaps: true })
        .pipe(
            plumber({
                errorHandler: notify.onError({
                    title: "JS Error",
                    message: "<%= error.message %>",
                }),
            })
        )
        // Просто копіюємо файли зі структурою
        .pipe(gulp.dest(paths.js.dest, { sourcemaps: "." }))
        .pipe(browserSync.stream());
}

// ========== МІНІМІЗАЦІЯ JS (для продакшну) ==========
export function minifyScripts() {
    return gulp
        .src(paths.js.src)
        .pipe(sourcemaps.init())
        .pipe(uglify())
        .pipe(
            rename(function (path) {
                // Додаємо .min перед розширенням
                path.basename += ".min";
            })
        )
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest(paths.js.dest));
}

// ========== ОПТИМІЗАЦІЯ ЗОБРАЖЕНЬ ==========
export function images() {
    return gulp
        .src(paths.images.src, { encoding: false })
        .pipe(
            imagemin([
                gifsicle({ interlaced: true }),
                mozjpeg({ quality: 80, progressive: true }),
                optipng({ optimizationLevel: 5 }),
                svgo({
                    plugins: [
                        {
                            name: "removeViewBox",
                            active: false,
                        },
                        {
                            name: "cleanupIDs",
                            active: false,
                        },
                    ],
                }),
            ])
        )
        .pipe(gulp.dest(paths.images.dest))
        .pipe(browserSync.stream());
}

// ========== КОПІЮВАННЯ ШРИФТІВ ==========
export function fonts() {
    return gulp
        .src(paths.fonts.src)
        .pipe(gulp.dest(paths.fonts.dest))
        .pipe(browserSync.stream());
}

// ========== BROWSER SYNC ==========
export function serve(done) {
    browserSync.init({
        proxy: "localhost:8000", // Django development server
        port: 3000,
        open: false,
        notify: false,
        ui: {
            port: 3001,
        },
    });
    done();
}

// ========== СПОСТЕРЕЖЕННЯ ЗА ФАЙЛАМИ ==========
export function watchFiles() {
    gulp.watch(paths.scss.watch, styles);
    gulp.watch(paths.tailwind.watch, tailwind);
    gulp.watch(paths.js.src, scripts);
    gulp.watch(paths.images.src, images);
    gulp.watch(paths.fonts.src, fonts);
    gulp.watch("templates/**/*.html").on("change", browserSync.reload);
}

// ========== ЗАВДАННЯ ==========

// Розробка (з browser-sync)
export const dev = gulp.series(
    clean,
    gulp.parallel(styles, tailwind, scripts, images, fonts),
    gulp.parallel(serve, watchFiles)
);

// Просто watch без browser-sync
export const watch = gulp.series(
    clean,
    gulp.parallel(styles, tailwind, scripts, images, fonts),
    watchFiles
);

// Продакшн збірка
export const build = gulp.series(
    clean,
    gulp.parallel(styles, tailwind, scripts, images, fonts),
    gulp.parallel(minifyStyles, minifyScripts)
);

// Дефолтна задача
export default dev;
