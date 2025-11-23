// gulpfile.js

import gulp from "gulp";
import gulpSass from "gulp-sass";
import * as dartSass from "sass";
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
    // CRM SCSS
    // crm_scss: {
    //   src: "static/src/scss/crm/main.scss",
    //   watch: "static/src/scss/crm/**/*.scss",
    //   dest: "static/dist/css/crm/",
    // },
    // USER SCSS
    // user_scss: {
    //   src: "static/src/scss/user/main.scss",
    //   watch: "static/src/scss/user/**/*.scss",
    //   dest: "static/dist/css/user/",
    // },
    // SCSS
    scss: {
        src: "static/src/scss/main.scss",
        watch: "static/src/scss/**/*.scss",
        dest: "static/dist/css/",
    },
    // TAILWIND
    tailwind: {
        src: "static/src/css/tailwind.css",
        watch: ["static/src/css/**/*.css", "templates/**/*.html", "**/*.py"],
        dest: "static/dist/css/libs/",
    },
    // CRM JAVASCRIPT
    crm_js: {
        src: "static/src/js/crm/**/*.js",
        watch: "static/src/js/crm/**/*.js",
        dest: "static/dist/js/crm/",
    },
    // USER JAVASCRIPT
    user_js: {
        src: "static/src/js/user/**/*.js",
        watch: "static/src/js/user/**/*.js",
        dest: "static/dist/js/user/",
    },
    // UTILITY JAVASCRIPT
    utility_js: {
        src: "static/src/js/utility/**/*.js",
        watch: "static/src/js/utility/**/*.js",
        dest: "static/dist/js/utility/",
    },
    // ЗОБРАЖЕННЯ
    images: {
        src: "static/src/img/**/*",
        dest: "static/dist/img/",
    },
    // ШРИФТИ
    fonts: {
        src: "static/src/fonts/**/*",
        dest: "static/dist/fonts/",
    },
};

// ========== ОЧИСТКА ==========
export function clean() {
    return deleteAsync(["static/dist/**", "!static/dist"]);
}

// ========== CRM SASS КОМПІЛЯЦІЯ ==========
// export function crmStyles() {
//   return gulp
//     .src(paths.crm_scss.src, { sourcemaps: true })
//     .pipe(
//       plumber({
//         errorHandler: notify.onError({
//           title: "CRM SCSS Error",
//           message: "<%= error.message %>",
//         }),
//       })
//     )
//     .pipe(
//       sass({
//         outputStyle: "expanded",
//         includePaths: ["node_modules", "static/src/scss/crm"],
//       }).on("error", sass.logError)
//     )
//     .pipe(
//       autoprefixer({
//         cascade: false,
//       })
//     )
//     .pipe(rename("style.css"))
//     .pipe(gulp.dest(paths.crm_scss.dest, { sourcemaps: "." }))
//     .pipe(browserSync.stream());
// }

// ========== USER SASS КОМПІЛЯЦІЯ ==========
// export function userStyles() {
    //   return gulp
    //     .src(paths.user_scss.src, { sourcemaps: true })
    //     .pipe(
        //       plumber({
            //         errorHandler: notify.onError({
                //           title: "USER SCSS Error",
                //           message: "<%= error.message %>",
                //         }),
                //       })
                //     )
                //     .pipe(
                    //       sass({
//         outputStyle: "expanded",
//         includePaths: ["node_modules", "static/src/scss/user"],
//       }).on("error", sass.logError)
//     )
//     .pipe(
    //       autoprefixer({
//         cascade: false,
//       })
//     )
//     .pipe(rename("style.css"))
//     .pipe(gulp.dest(paths.user_scss.dest, { sourcemaps: "." }))
//     .pipe(browserSync.stream());
// }


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
                includePaths: ["node_modules", "static/src/scss"],
            }).on("error", sass.logError)
        )
        .pipe(
            autoprefixer({
                cascade: false,
            })
        )
        .pipe(rename("style.css"))
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

// ========== МІНІМІЗАЦІЯ CRM CSS (для продакшну) ==========
// export function minifyCrmStyles() {
//   return gulp
//     .src("static/dist/css/crm/style.css")
//     .pipe(sourcemaps.init({ loadMaps: true }))
//     .pipe(
//       cleanCSS({
//         level: 2,
//         compatibility: "ie11",
//       })
//     )
//     .pipe(
//       rename({
//         suffix: ".min",
//       })
//     )
//     .pipe(sourcemaps.write("."))
//     .pipe(gulp.dest(paths.crm_scss.dest));
// }

// ========== МІНІМІЗАЦІЯ USER CSS (для продакшну) ==========
// export function minifyUserStyles() {
    //   return gulp
    //     .src("static/dist/css/user/style.css")
    //     .pipe(sourcemaps.init({ loadMaps: true }))
    //     .pipe(
        //       cleanCSS({
            //         level: 2,
            //         compatibility: "ie11",
            //       })
            //     )
            //     .pipe(
                //       rename({
//         suffix: ".min",
//       })
//     )
//     .pipe(sourcemaps.write("."))
//     .pipe(gulp.dest(paths.user_scss.dest));
// }


// ========== МІНІМІЗАЦІЯ CSS (для продакшну) ==========
export function minifyStyles() {
    return gulp
        .src("static/dist/css/style.css")
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
        .pipe(gulp.dest(paths.user_scss.dest));
}

// ========== МІНІМІЗАЦІЯ TAILWIND CSS (для продакшну) ==========
export function minifyTailwind() {
    return gulp
        .src("static/dist/css/libs/tailwind.css")
        .pipe(sourcemaps.init({ loadMaps: true }))
        .pipe(
            cleanCSS({
                level: 2,
            })
        )
        .pipe(
            rename({
                suffix: ".min",
            })
        )
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest(paths.tailwind.dest));
}

// ========== CRM JAVASCRIPT - ОПТИМІЗАЦІЯ БЕЗ ОБ'ЄДНАННЯ ==========
export function crmScripts() {
    return gulp
        .src(paths.crm_js.src, { sourcemaps: true })
        .pipe(
            plumber({
                errorHandler: notify.onError({
                    title: "CRM JS Error",
                    message: "<%= error.message %>",
                }),
            })
        )
        .pipe(gulp.dest(paths.crm_js.dest, { sourcemaps: "." }))
        .pipe(browserSync.stream());
}

// ========== USER JAVASCRIPT - ОПТИМІЗАЦІЯ БЕЗ ОБ'ЄДНАННЯ ==========
export function userScripts() {
    return gulp
        .src(paths.user_js.src, { sourcemaps: true })
        .pipe(
            plumber({
                errorHandler: notify.onError({
                    title: "USER JS Error",
                    message: "<%= error.message %>",
                }),
            })
        )
        .pipe(gulp.dest(paths.user_js.dest, { sourcemaps: "." }))
        .pipe(browserSync.stream());
}

// ========== UTILITY JAVASCRIPT - ОПТИМІЗАЦІЯ БЕЗ ОБ'ЄДНАННЯ ==========
export function utilityScripts() {
    return gulp
        .src(paths.utility_js.src, { sourcemaps: true })
        .pipe(
            plumber({
                errorHandler: notify.onError({
                    title: "UTILITY JS Error",
                    message: "<%= error.message %>",
                }),
            })
        )
        .pipe(gulp.dest(paths.utility_js.dest, { sourcemaps: "." }))
        .pipe(browserSync.stream());
}


// ========== МІНІМІЗАЦІЯ CRM JS (для продакшну) ==========
export function minifyCrmScripts() {
    return gulp
        .src(paths.crm_js.src)
        .pipe(sourcemaps.init())
        .pipe(
            plumber({
                errorHandler: notify.onError({
                    title: "CRM JS Minify Error",
                    message: "<%= error.message %>",
                }),
            })
        )
        .pipe(uglify())
        .pipe(
            rename(function (path) {
                path.basename += ".min";
            })
        )
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest(paths.crm_js.dest));
}

// ========== МІНІМІЗАЦІЯ USER JS (для продакшну) ==========
export function minifyUserScripts() {
    return gulp
        .src(paths.user_js.src)
        .pipe(sourcemaps.init())
        .pipe(
            plumber({
                errorHandler: notify.onError({
                    title: "USER JS Minify Error",
                    message: "<%= error.message %>",
                }),
            })
        )
        .pipe(uglify())
        .pipe(
            rename(function (path) {
                path.basename += ".min";
            })
        )
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest(paths.user_js.dest));
}

// ========== МІНІМІЗАЦІЯ UTILITY JS (для продакшну) ==========
export function minifyUtilityScripts() {
    return gulp
        .src(paths.utility_js.src)
        .pipe(sourcemaps.init())
        .pipe(
            plumber({
                errorHandler: notify.onError({
                    title: "UTILITY JS Minify Error",
                    message: "<%= error.message %>",
                }),
            })
        )
        .pipe(uglify())
        .pipe(
            rename(function (path) {
                path.basename += ".min";
            })
        )
        .pipe(sourcemaps.write("."))
        .pipe(gulp.dest(paths.utility_js.dest))
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
        // Додаткові налаштування для Django
        files: [
            "templates/**/*.html",
            "static/dist/**/*",
        ],
        watchEvents: ["change", "add", "unlink", "addDir", "unlinkDir"],
    });
    done();
}

// ========== СПОСТЕРЕЖЕННЯ ЗА ФАЙЛАМИ ==========
export function watchFiles() {
    // gulp.watch(paths.crm_scss.watch, crmStyles);
    // gulp.watch(paths.user_scss.watch, userStyles);
    gulp.watch(paths.scss.watch, styles);
    gulp.watch(paths.tailwind.watch, tailwind);
    gulp.watch(paths.crm_js.watch, crmScripts);
    gulp.watch(paths.user_js.watch, userScripts);
    gulp.watch(paths.utility_js.watch, utilityScripts);
    gulp.watch(paths.images.src, images);
    gulp.watch(paths.fonts.src, fonts);
    gulp.watch("templates/**/*.html").on("change", browserSync.reload);
}

// ========== ЗАВДАННЯ ==========

// Розробка (з browser-sync)
export const dev = gulp.series(
    clean,
    // gulp.parallel(crmStyles, userStyles, tailwind, crmScripts, userScripts, utilityScripts, images, fonts),
    gulp.parallel(styles, tailwind, crmScripts, userScripts, utilityScripts, images, fonts),
    gulp.parallel(serve, watchFiles)
);

// Просто watch без browser-sync
export const watch = gulp.series(
    clean,
    // gulp.parallel(crmStyles, userStyles, tailwind, crmScripts, userScripts, utilityScripts, images, fonts),
    gulp.parallel(styles, tailwind, crmScripts, userScripts, utilityScripts, images, fonts),
    // watchFiles
);

// Продакшн збірка
export const build = gulp.series(
    clean,
    // gulp.parallel(crmStyles, userStyles, tailwind, crmScripts, userScripts, utilityScripts, images, fonts),
    gulp.parallel(styles, tailwind, crmScripts, userScripts, utilityScripts, images, fonts),
    // gulp.parallel(minifyCrmStyles, minifyUserStyles, minifyTailwind, minifyCrmScripts, minifyUserScripts, minifyUtilityScripts)
    gulp.parallel(minifyStyles, minifyTailwind, minifyCrmScripts, minifyUserScripts, minifyUtilityScripts)
);

// Дефолтна задача
export default dev;
