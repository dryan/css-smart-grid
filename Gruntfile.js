module.exports  =   function(grunt) {
    grunt.initConfig({
        pkg: grunt.file.readJSON('package.json'),
        sass: {
            dist: {
                files: {
                    'css/smart-grid.css': 'sass/smart-grid.scss',
                    'css/smart-grid-flexbox.css': 'sass/smart-grid-flexbox.scss',
                    'css/docs.css': 'sass/docs.scss'
                }
            },
            options: {
                loadPath: [
                    'bower_components/bourbon/dist'
                ],
                style: 'compressed'
            }
        },
        watch: {
            css: {
                files: 'sass/*.scss',
                tasks: ['sass']
            }
        }
    });
    grunt.loadNpmTasks('grunt-contrib-sass');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.registerTask('default', ['watch']);
    grunt.registerTask('build', ['sass']);
};
