define(["eloue/app",
        "eloue/modules/booking/controllers/ProductDetailsCtrl",
        "eloue/modules/booking/directives/ProductDetailsBookingDirective",
        "eloue/modules/booking/directives/BookingModalDirective",
        "eloue/modules/booking/directives/MessageModalDirective",
        "eloue/modules/booking/directives/PhoneModalDirective",
        "eloue/modules/booking/directives/ProductDetailsSmallDirective",
        "../../common/eloue/services", "../../common/eloue/controllers", "../../common/eloue/directives", "../../common/eloue/interceptors"],
    function (EloueApp) {
        "use strict";

        /**
         * Routing configuration for app.
         */
        EloueApp.config([
            "$stateProvider",
            "$urlRouterProvider",
            "$httpProvider",
            function ($stateProvider, $urlRouterProvider, $httpProvider) {
                //TODO: define proper routes for pop-ins



                // push function to the responseInterceptors which will intercept
                // the http responses of the whole application
                $httpProvider.responseInterceptors.push("ErrorHandlerInterceptor");
            }
        ]);

        EloueApp.run(["$rootScope", "$location", "$route", "$http", "AuthService", function ($rootScope, $location, $route, $http, AuthService) {
            AuthService.saveAttemptUrl();
            var userToken = AuthService.getCookie("user_token");
            $http.defaults.useXDomain = true;
            delete $http.defaults.headers.common['X-Requested-With'];
            if (userToken && userToken.length > 0) {
                $http.defaults.headers.common.authorization = "Bearer " + userToken;
            }

            // Route change event listener
            $rootScope.$on("$locationChangeStart", function (event, next, current) {
                // Redirect not authenticated user
                var routes = $route.routes;
                for (var i in routes) {
                    if (next.indexOf(i) != -1) {
                        if (routes[i].secure && !AuthService.isLoggedIn()) {
                            $rootScope.$broadcast("redirectToLogin");
                            event.preventDefault();
                        }
                    }
                }
            });

            $rootScope.$on("redirectToLogin", function () {
                $location.path("/");
            });
        }]);
    });