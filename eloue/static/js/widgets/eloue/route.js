define(["eloue/app",
        "eloue/modules/booking/controllers/ProductDetailsCtrl",
        "eloue/modules/booking/controllers/PublishAdCtrl",
        "../../common/eloue/services", "../../common/eloue/controllers", "../../common/eloue/directives", "../../common/eloue/interceptors"],
    function (EloueApp) {
        "use strict";

        /**
         * Routing configuration for app.
         */
        EloueApp.config([
            "$routeProvider",
            "$httpProvider",
            function ($routeProvider, $httpProvider) {
                $routeProvider
                    .when('/login', {
                        templateUrl: 'modalContainer',
                        controller: 'ModalCtrl',
                        secure: false
                    })
                    .when('/registration', {
                        templateUrl: 'modalContainer',
                        controller: 'ModalCtrl',
                        secure: false
                    })
                    .when('/booking', {
                        templateUrl: 'modalContainer',
                        controller: 'ModalCtrl',
                        secure: true
                    })
                    .when('/message', {
                        templateUrl: 'modalContainer',
                        controller: 'ModalCtrl',
                        secure: true
                    })
                    .when('/phone', {
                        templateUrl: 'modalContainer',
                        controller: 'ModalCtrl',
                        secure: true
                    })
                    .when('/publish', {
                        templateUrl: 'modalContainer',
                        controller: 'ModalCtrl',
                        secure: true
                    })
                    .otherwise({redirectTo: '/'});

                // push function to the interceptors which will intercept
                // the http responses of the whole application
                $httpProvider.interceptors.push("ErrorHandlerInterceptor");
            }
        ]);

        EloueApp.run(["$rootScope", "$location", "$route", "$http", "AuthService", function ($rootScope, $location, $route, $http, AuthService) {
            var userToken = AuthService.getCookie("user_token");
            $http.defaults.useXDomain = true;
            delete $http.defaults.headers.common['X-Requested-With'];
            if (userToken && userToken.length > 0) {
                $http.defaults.headers.common.authorization = "Bearer " + userToken;
            }
            var csrftoken = AuthService.getCookie('csrftoken');
            if (csrftoken && csrftoken.length > 0) {
                $http.defaults.headers.common["X-CSRFToken"] = csrftoken;
            }

            $rootScope.$on("redirectToLogin", function () {
                $location.path("/login");
            });
        }]);
    });