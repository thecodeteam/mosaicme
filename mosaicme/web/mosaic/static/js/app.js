
var mosaicmeApp = angular.module('mosaicmeApp', []).config(function($httpProvider) {

    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

});

mosaicmeApp.controller('MosaicMeCtrl', function ($scope) {

    $scope.images = [
        {'url': 'http://charleshood.net/wp-content/uploads/2010/05/IMG_2080.jpg'},
        {'url': 'https://infocus.emc.com/wp-content/uploads/2013/06/8717630635_4d7c4bb014_z.jpg'},
        {'url': 'https://jasonnash.files.wordpress.com/2012/05/lab-2.jpg'},
        {'url': 'https://i.vimeocdn.com/video/437533496_640.jpg'},
        {'url': 'https://oxygencloudblog.files.wordpress.com/2011/05/img_0016.jpg'},
        {'url': 'http://blogs.cisco.com/wp-content/uploads/935566_10151574064859817_836422499_n-550x365.jpg'}
    ];
});