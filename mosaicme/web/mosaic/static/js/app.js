var mosaicmeApp = angular.module('mosaicmeApp', ['ui.bootstrap', 'ngRoute', 'angularMoment', 'cgBusy']).config(function ($httpProvider) {

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
            })
            .when('/learn-more', {
                templateUrl: 'static/partials/learn-more.html'
            })
            .otherwise({
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
    .directive('ngElevateZoom', function () {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                console.log("Linking")

                //Will watch for changes on the attribute
                attrs.$observe('zoomImage', function () {
                    linkElevateZoom();
                });

                function linkElevateZoom() {
                    //Check if its not empty
                    if (!attrs.zoomImage) return;

                    $('#mosaic-loading-bar').remove();

                    element.attr('data-zoom-image', attrs.zoomImage);
                    $(element).elevateZoom({
                        zoomType: "lens",
                        lensShape: "round",
                        lensSize: 200,
                        scrollZoom: true
                    });
                }

                linkElevateZoom();

            }
        };
    })
    .directive('zoomContainer', function () {
        return {
            restrict: 'A',
            link: function (scope, element, attrs) {
                scope.$on('$routeChangeSuccess', function () {

                    var target = element.children('div.zoomContainer').remove();
                })
            }
        }

    })
    .directive('onThumbnailLoaded', function () {
        return {
            link: function(scope, element, attrs) {
                element.bind("load" , function(e){
                    var imgClass = (this.width / this.height > 1) ? 'wide' : 'tall';
                    $(this).addClass(imgClass);
                });
            }
        }
    })
    .controller('HeaderCtrl', ['$scope', '$location',
        function ($scope, $location) {

            $scope.isActive = function (viewLocation) {
                return viewLocation === $location.path();
            };
        }
    ])
    .controller('MainCtrl', ['$scope', '$http', '$log', '$filter', function ($scope, $http, $log, $filter) {

        var orderBy = $filter('orderBy');

        if (typeof twttr != 'undefined') {
            twttr.widgets.load();
        }

        $scope.carouselInterval = 3000;

        $scope.pageChanged = function () {
            $log.log('Page changed to: ' + $scope.currentPage);

            var start = ($scope.currentPage - 1) * $scope.itemsPerPage;
            $scope.displayImages = $scope.allImages.slice(start, start + $scope.itemsPerPage);
        };

        $scope.currentPage = 1;
        $scope.itemsPerPage = 8;

        $scope.loadPromise = $http.get('/mosaic').
            success(function (data, status, headers, config) {
                $scope.allImages = data['mosaics'];
                $scope.allImages = orderBy($scope.allImages, '-date', false);

                $scope.latestImages = $scope.allImages.slice(0, 5);
                $scope.totalItems = data['size'];

                $scope.loaded = true;
                $scope.pageChanged();
            }).
            error(function (data, status, headers, config) {
                alert('Error getting images!');
            });

    }])
    .controller('MosaicDetailsCtrl', ['$scope', '$http', '$routeParams',
        function ($scope, $http, $routeParams) {

            $scope.loadPromise = $http.get('/mosaic/' + $routeParams.mosaicId).
                success(function (data, status, headers, config) {
                    $scope.urlSmall = data['url_small'];
                    $scope.urlLarge = data['url_large'];
                    $scope.username = data['username'];
                    $scope.createdAt = data['date'];

                    $scope.loaded = true;
                }).
                error(function (data, status, headers, config) {
                    alert('Error getting the mosaic!');
                });


            $scope.$on("$destroy", function () {
                $('#mosaic-img').remove();
            });

        }]);
