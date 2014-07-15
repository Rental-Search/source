
define(["eloue/app", "eloue/modules/user_management/services/AuthService",
        "eloue/modules/user_management/controllers/LoginCtrl",
        "eloue/modules/user_management/controllers/RegisterCtrl",
        "eloue/modules/dashboard/controllers/DashboardCtrl",
        "eloue/modules/product_details/controllers/ProductDetailsCtrl",
        "eloue/modules/user_management/directives/LoginFormDirective",
        "eloue/modules/user_management/directives/RegistrationFormDirective",
        "eloue/modules/user_management/directives/validation/PasswordMatchDirective",
        "eloue/modules/product_details/directives/ProductDetailsBookingDirective",
        "eloue/modules/product_details/directives/BookingModalDirective",
        "eloue/modules/product_details/directives/MessageModalDirective",
        "eloue/modules/product_details/directives/PhoneModalDirective",
        "eloue/modules/product_details/directives/validation/DatepickerDirective",
        "eloue/modules/product_details/directives/validation/TimepickerDirective"],
    function (EloueApp) {

        "use strict";
        /**
         * Routing configuration for app module.
         */
        EloueApp.config(function ($routeProvider) {
            $routeProvider
                .when("/", {
                    templateUrl: "views/main.html"
                })
                .when("/dashboard", {
                    templateUrl: "/scripts/eloue/modules/dashboard/views/dashboard.html",
                    controller: "DashboardCtrl",
                    secure: true //this route is secured
                })
                .when("/product/:productId", {
                    templateUrl: "/scripts/eloue/modules/product_details/views/product-details.html",
                    controller: "ProductDetailsCtrl"
                })
                .otherwise({
                    redirectTo: "/"
                });
        });

        EloueApp.run(["$rootScope", "$location", "$route", "AuthService", function ($rootScope, $location, $route, AuthService) {

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
                console.log("Redirect to login");
                $location.path("/");
            });
        }]);
    });