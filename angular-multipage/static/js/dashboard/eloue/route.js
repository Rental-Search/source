"use strict";

define(["eloue/app",
        "eloue/controllers/DashboardRootCtrl",
        "eloue/controllers/DashboardCtrl",
        "eloue/controllers/MessagesCtrl",
        "eloue/controllers/BookingsCtrl",
        "eloue/controllers/ItemsCtrl",
        "eloue/controllers/AccountCtrl",
        "eloue/controllers/account/AccountProfileCtrl",
        "eloue/controllers/account/AccountVerificationCtrl",
        "eloue/controllers/account/AccountAddressesCtrl",
        "eloue/controllers/account/AccountPhonesCtrl",
        "eloue/controllers/account/AccountPaymentsCtrl",
        "eloue/controllers/account/AccountPasswordCtrl",
        "eloue/controllers/account/AccountInvitationCtrl",
        "eloue/controllers/messages/MessageDetailCtrl",
        "eloue/directives/FileChooserDirective"],
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
                    })
                    .state("account.profile", {
                        url: "/profile",
                        templateUrl: "partials/dashboard/account/profile.html",
                        controller: "AccountProfileCtrl"
                    })
                    .state("account.verification", {
                        url: "/verification",
                        templateUrl: "partials/dashboard/account/verification.html",
                        controller: "AccountVerificationCtrl"
                    })
                    .state("account.addresses", {
                        url: "/addresses",
                        templateUrl: "partials/dashboard/account/addresses.html",
                        controller: "AccountAddressesCtrl"
                    })
                    .state("account.phones", {
                        url: "/phones",
                        templateUrl: "partials/dashboard/account/phones.html",
                        controller: "AccountPhonesCtrl"
                    })
                    .state("account.payments", {
                        url: "/payments",
                        templateUrl: "partials/dashboard/account/payments.html",
                        controller: "AccountPaymentsCtrl"
                    })
                    .state("account.password", {
                        url: "/password",
                        templateUrl: "partials/dashboard/account/password.html",
                        controller: "AccountPasswordCtrl"
                    })
                    .state("account.invitation", {
                        url: "/invitation",
                        templateUrl: "partials/dashboard/account/invitation.html",
                        controller: "AccountInvitationCtrl"
                    })
                    .state("messages.detail", {
                        url: "/:id",
                        templateUrl: "partials/dashboard/messages/message_detail.html",
                        controller: "MessageDetailCtrl"
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