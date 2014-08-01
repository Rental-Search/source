
define(["eloue/app", "eloue/modules/user_management/services/AuthService",
        "eloue/modules/user_management/controllers/LoginCtrl",
        "eloue/modules/user_management/controllers/RegisterCtrl",
        "eloue/modules/dashboard/controllers/DashboardCtrl",
        "eloue/modules/booking/controllers/ProductDetailsCtrl",
        "eloue/modules/user_management/directives/LoginFormDirective",
        "eloue/modules/user_management/directives/RegistrationFormDirective",
        "eloue/modules/user_management/directives/validation/PasswordMatchDirective",
        "eloue/modules/booking/directives/ProductDetailsBookingDirective",
        "eloue/modules/booking/directives/BookingModalDirective",
        "eloue/modules/booking/directives/MessageModalDirective",
        "eloue/modules/booking/directives/PhoneModalDirective",
        "eloue/modules/booking/directives/ProductDetailsSmallDirective",
        "eloue/modules/booking/directives/validation/DatetimepickerDirective"],
    function (EloueApp) {

        "use strict";
        /**
         * Routing configuration for app module.
         */
        EloueApp.config(function ($routeProvider) {
            $routeProvider
                .when("/", {
                    templateUrl: "views/dashboard.html"
                })
                .when("/dashboard", {
                    templateUrl: "/scripts/eloue/modules/dashboard/views/dashboard.html",
                    controller: "DashboardCtrl",
                    secure: true //this route is secured
                })
                .when("/product/:productId", {
                    templateUrl: "/scripts/eloue/modules/booking/views/product-details.html",
                    controller: "ProductDetailsCtrl"
                })
                .otherwise({
                    redirectTo: "/"
                });
        });

        EloueApp.run(["$rootScope", "$location", "$route", "$http", "AuthService", function ($rootScope, $location, $route, $http, AuthService) {
            var userToken = AuthService.getCookie("user_token");
            $http.defaults.useXDomain = true;
            delete $http.defaults.headers.common['X-Requested-With'];
            $http.defaults.headers.common.authorization = "Bearer " + userToken;

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

            $rootScope.$on("redirectToLogin", function() {
                $location.path("/");
            });
        }]);
    });