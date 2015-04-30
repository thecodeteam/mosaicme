var mosaicmeApp = angular.module('mosaicmeApp', ['ui.bootstrap', 'ngRoute']).config(function ($httpProvider) {

    $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';

});

mosaicmeApp
    .config(function ($routeProvider) {
        $routeProvider

            // route for the home page
            .when('/', {
                templateUrl: 'static/partials/main.html',
                controller: 'MainCtrl'
            })
            .when('/mosaic/:mosaicId', {
                templateUrl: 'static/partials/mosaic-detail.html',
                controller: 'MosaicDetailsCtrl'
            }).
            otherwise({
                redirectTo: '/'
            });
    })
    .directive('onLastRepeat', function () {
        return function (scope, element, attrs) {
            if (scope.$last) setTimeout(function () {
                scope.$emit('onRepeatLast', element, attrs);
            }, 1);
        };
    })
    .directive('imageOnLoad', function () {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                element.bind('load', function () {
                    $("#mosaic-img").elevateZoom({
                        zoomType: "lens",
                        lensShape: "round",
                        lensSize: 200,
                        scrollZoom : true
                    });
                });
            }
        };
    })
    .controller('MainCtrl', ['$scope', '$http', '$log', function ($scope, $http, $log) {

        $scope.carouselInterval = 3000;

        $scope.pageChanged = function () {
            $log.log('Page changed to: ' + $scope.currentPage);

            var start = ($scope.currentPage - 1) * $scope.itemsPerPage;
            $scope.displayImages = $scope.allImages.slice(start, start + $scope.itemsPerPage);

        };

        $scope.currentPage = 1;
        $scope.itemsPerPage = 8;

        $http.get('/mosaic').
            success(function (data, status, headers, config) {
                $scope.allImages = data['images'];
                $scope.totalItems = data['size'];

                $scope.pageChanged();
            }).
            error(function (data, status, headers, config) {
                alert('Error getting images!');
            });

    }])
    .controller('MosaicDetailsCtrl', ['$scope', '$http', '$routeParams',
        function ($scope, $http, $routeParams) {

            $http.get('/mosaic/' + $routeParams.mosaicId).
                success(function (data, status, headers, config) {
                    $scope.imageUrl = data['url'];
                }).
                error(function (data, status, headers, config) {
                    alert('Error getting the mosaic!');
                });

        }]);
