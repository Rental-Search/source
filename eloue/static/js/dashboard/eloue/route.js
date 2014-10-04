"use strict";

define(["eloue/app",
        "eloue/controllers/DashboardRootCtrl",
        "eloue/controllers/DashboardCtrl",
        "eloue/controllers/MessagesCtrl",
        "eloue/controllers/BookingsCtrl",
        "eloue/controllers/ItemsCtrl",
        "eloue/controllers/items/ItemsInfoCtrl",
        "eloue/controllers/items/ItemsCalendarCtrl",
        "eloue/controllers/items/ItemsProfitsCtrl",
        "eloue/controllers/items/ItemsTariffsCtrl",
        "eloue/controllers/items/ItemsTermsCtrl",
        "eloue/controllers/items/ItemsTabsCtrl",
        "eloue/controllers/AccountCtrl",
        "eloue/controllers/account/AccountProfileCtrl",
        "eloue/controllers/account/AccountVerificationCtrl",
        "eloue/controllers/account/AccountAddressesCtrl",
        "eloue/controllers/account/AccountAddressDetailCtrl",
        "eloue/controllers/account/AccountPhonesCtrl",
        "eloue/controllers/account/AccountPaymentsCtrl",
        "eloue/controllers/account/AccountPasswordCtrl",
        "eloue/controllers/account/AccountInvitationCtrl",
        "eloue/controllers/messages/MessageDetailCtrl",
        "eloue/controllers/bookings/BookingDetailCtrl",
        "eloue/controllers/DashboardLoginCtrl",
        "eloue/directives/FileChooserDirective",
        "../../common/eloue/interceptors"],
    function (EloueApp) {

        /**
         * Routing configuration for app.
         */
        EloueApp.config([
            "$stateProvider",
            "$urlRouterProvider",
            "$httpProvider",
            function ($stateProvider, $urlRouterProvider, $httpProvider) {

                $urlRouterProvider.otherwise("/");

                $stateProvider
                    .state("login", {
                        url: "/login",
                        templateUrl: "partials/dashboard/login.html",
                        controller: "DashboardLoginCtrl",
                        insecure: true
                    })
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
                    .state("messages.detail", {
                        url: "/:id",
                        templateUrl: "partials/dashboard/messages/message_detail.html",
                        controller: "MessageDetailCtrl"
                    })
                    .state("bookings", {
                        url: "/bookings",
                        templateUrl: "partials/dashboard/bookings.html",
                        controller: "BookingsCtrl"
                    })
                    .state("bookings.detail", {
                        url: "/:uuid",
                        templateUrl: "partials/dashboard/bookings/booking_detail.html",
                        controller: "BookingDetailCtrl"
                    })
                    .state("items", {
                        url: "/items",
                        templateUrl: "partials/dashboard/items.html",
                        controller: "ItemsCtrl"
                    })
                    .state("items.info", {
                        url: "/:id/info",
                        views: {
                            "": {
                                templateUrl: "partials/dashboard/items/item_detail.html"
                            },
                            "tabs@items.info": {
                                templateUrl: "partials/dashboard/items/tabs.html",
                                controller: "ItemsTabsCtrl"
                            },
                            "details@items.info": {
                                templateUrl: "partials/dashboard/items/info.html",
                                controller: "ItemsInfoCtrl"
                            }
                        }
                    })
                    .state("items.calendar", {
                        url: "/:id/calendar",
                        views: {
                            "": {
                                templateUrl: "partials/dashboard/items/item_detail.html"
                            },
                            "tabs@items.calendar": {
                                templateUrl: "partials/dashboard/items/tabs.html",
                                controller: "ItemsTabsCtrl"
                            },
                            "details@items.calendar": {
                                templateUrl: "partials/dashboard/items/calendar.html",
                                controller: "ItemsCalendarCtrl"
                            }
                        }
                    })
                    .state("items.tariffs", {
                        url: "/:id/tariffs",
                        views: {
                            "": {
                                templateUrl: "partials/dashboard/items/item_detail.html"
                            },
                            "tabs@items.tariffs": {
                                templateUrl: "partials/dashboard/items/tabs.html",
                                controller: "ItemsTabsCtrl"
                            },
                            "details@items.tariffs": {
                                templateUrl: "partials/dashboard/items/tariffs.html",
                                controller: "ItemsTariffsCtrl"
                            }
                        }
                    })
                    .state("items.terms", {
                        url: "/:id/terms",
                        views: {
                            "": {
                                templateUrl: "partials/dashboard/items/item_detail.html"
                            },
                            "tabs@items.terms": {
                                templateUrl: "partials/dashboard/items/tabs.html",
                                controller: "ItemsTabsCtrl"
                            },
                            "details@items.terms": {
                                templateUrl: "partials/dashboard/items/terms.html",
                                controller: "ItemsTermsCtrl"
                            }
                        }
                    })
                    .state("items.profits", {
                        url: "/:id/profits",
                        views: {
                            "": {
                                templateUrl: "partials/dashboard/items/item_detail.html"
                            },
                            "tabs@items.profits": {
                                templateUrl: "partials/dashboard/items/tabs.html",
                                controller: "ItemsTabsCtrl"
                            },
                            "details@items.profits": {
                                templateUrl: "partials/dashboard/items/profits.html",
                                controller: "ItemsProfitsCtrl"
                            }
                        }
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
                    .state("account.addresses.detail", {
                        url: "/:id",
                        templateUrl: "partials/dashboard/account/address_detail.html",
                        controller: "AccountAddressDetailCtrl"
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
                    });




                // push function to the responseInterceptors which will intercept
                // the http responses of the whole application
                $httpProvider.responseInterceptors.push("ErrorHandlerInterceptor");
            }
        ]);

        EloueApp.run(["$rootScope", "$route", "$http", "$state", "AuthService", function ($rootScope, $route, $http, $state, AuthService) {
            AuthService.saveAttemptUrl();
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

            if (userToken && userToken.length > 0) {
                $http.defaults.headers.common.Authorization = "Bearer " + userToken;
            }

            var csrftoken = AuthService.getCookie('csrftoken');
            if (csrftoken && csrftoken.length > 0) {
                $http.defaults.headers.common["X-CSRFToken"] = csrftoken;
            }

            // Route change event listener
            $rootScope.$on('$stateChangeStart',
                function(event, toState, toParams, fromState, fromParams){
                    if (!toState.insecure && !AuthService.isLoggedIn()) {
                        $rootScope.$broadcast("redirectToLogin");
                        event.preventDefault();
                    }
            });

            /**
             * Catch "redirectToLogin" event
             */
            $rootScope.$on("redirectToLogin", function() {
                $state.go("login");
            });
        }]);
    });