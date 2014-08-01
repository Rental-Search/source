"use strict";

define(["eloue/app",
        "eloue/controllers/DashboardRootCtrl",
        "eloue/controllers/DashboardCtrl",
        "eloue/controllers/MessagesCtrl",
        "eloue/controllers/BookingsCtrl",
        "eloue/controllers/ItemsCtrl",
        "eloue/controllers/AccountCtrl"],
    function (EloueApp) {

        /**
         * Routing configuration for app.
         */
        EloueApp.config(function ($routeProvider) {
            $routeProvider
                .when("/", {
                    templateUrl: "partials/dashboard/dashboard.html",
                    controller: "DashboardCtrl"
                })
                .when("/messages", {
                    templateUrl: "partials/dashboard/messages.html",
                    controller: "MessagesCtrl"
                })
                .when("/bookings", {
                    templateUrl: "partials/dashboard/bookings.html",
                    controller: "BookingsCtrl"
                })
                .when("/items", {
                    templateUrl: "partials/dashboard/items.html",
                    controller: "ItemsCtrl"
                })
                .when("/account", {
                    templateUrl: "partials/dashboard/account.html",
                    controller: "AccountCtrl"
                })
                .otherwise({
                    redirectTo: "/"
                });
        });

        EloueApp.run(["$rootScope", "$route", "$http", function ($rootScope, $route, $http) {
            var userToken = "";
            var name = "user_token=";
            var ca = document.cookie.split(';');
            for (var i = 0; i < ca.length; i++) {
                var c = ca[i];
                while (c.charAt(0) == ' ') c = c.substring(1);
                if (c.indexOf(name) != -1) {
                    userToken = c.substring(name.length, c.length);
                }
            }
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
                            //TODO: redirect to login
                            event.preventDefault();
                        }
                    }
                }
            });
        }]);
    });