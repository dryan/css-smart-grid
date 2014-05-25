module.exports  =   function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        sass: {
            dist: {
                files: {
                    'css/smart-grid.css': 'sass/smart-grid.scss',
                    'css/smart-grid-flexbox.css': 'sass/smart-grid-flexbox.scss'
                }
            },
            options: {
                sourcemap: true,
                style: 'compressed',
                banner: '/*! <%= pkg.name %> <%= pkg.version %> | <%= pkg.license %> | <%= pkg.homepage %> */'
            }
        },
        watch: {
            css: {
                files: 'sass/*.scss',
                tasks: ['sass']
            }
        },
        bump: {
            options: {
                files: ['package.json', 'bower.json'],
                commit: true,
                commitMessage: 'Release %VERSION%',
                commitFiles: ['package.json', 'bower.json', 'sass/*', 'css/*'],
                createTag: true,
                tagName: '%VERSION%',
                tagMessage: 'Release %VERSION%',
                push: true,
                pushTo: 'origin'
            }
        }
    });
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-bump');
    grunt.registerTask('default', ['watch']);
    grunt.registerTask('build', ['sass']);
    grunt.registerTask('rev:patch', ['bump-only:patch', 'sass', 'bump-commit']);
    grunt.registerTask('rev:minor', ['bump-only:minor', 'sass', 'bump-commit']);
    grunt.registerTask('rev:major', ['bump-only:major', 'sass', 'bump-commit']);
    grunt.registerTask('rev',       ['rev:patch']);
};
