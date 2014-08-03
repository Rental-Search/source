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
        EloueApp.config([
            "$stateProvider",
            "$urlRouterProvider",
            function ($stateProvider, $urlRouterProvider) {

                $urlRouterProvider.otherwise("/");

                $stateProvider
                    .state("dashboard", {
                        url: "/",
                        templateUrl: "partials/dashboard/dashboard.html",
                        controller: "DashboardCtrl"
                    })
                    .state("messages", {
                        url: "/messages",
                        templateUrl: "partials/dashboard/messages.html",
                        controller: "MessagesCtrl"
                    })
                    .state("bookings", {
                        url: "/bookings",
                        templateUrl: "partials/dashboard/bookings.html",
                        controller: "BookingsCtrl"
                    })
                    .state("items", {
                        url: "/items",
                        templateUrl: "partials/dashboard/items.html",
                        controller: "ItemsCtrl"
                    })
                    .state("account", {
                        url: "/account",
                        templateUrl: "partials/dashboard/account.html",
                        controller: "AccountCtrl"
                    });
            }
        ]);

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