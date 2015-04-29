var mosaicmeApp = angular.module('mosaicmeApp', ['ui.bootstrap']).config(function ($httpProvider) {

    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

});

mosaicmeApp
    .directive('onLastRepeat', function () {
        return function (scope, element, attrs) {
            if (scope.$last) setTimeout(function () {
                scope.$emit('onRepeatLast', element, attrs);
            }, 1);
        };
    })
    .controller('MosaicMeCtrl', function ($scope, $http, $log) {

        $scope.$on('onRepeatLast', function (scope, element, attrs) {
            $("#carousel1").tiksluscarousel(
                {
                    width: 0,
                    height: 0,
                    nav: 'thumbnails',
                    current: 1,
                    autoplayInterval: 5000,
                    loader: 'static/images/ajax-loader.gif'
                });
            });

        $scope.pageChanged = function() {
            $log.log('Page changed to: ' + $scope.currentPage);

            var start = ($scope.currentPage-1) * $scope.itemsPerPage;
            $scope.displayImages = $scope.allImages.slice(start, start + $scope.itemsPerPage);

        };

        $scope.currentPage = 1;
        $scope.itemsPerPage = 2;

        $http.get('/mosaic').
            success(function (data, status, headers, config) {
                $scope.allImages = data['images'];
                $scope.totalItems = data['size'];

                $scope.pageChanged();
            }).
            error(function (data, status, headers, config) {
                alert('Error getting images!');
            });

    });