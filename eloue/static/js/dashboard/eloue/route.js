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
        "eloue/controllers/items/ItemsShippingCtrl",
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
        "eloue/controllers/messages/NewMessageThreadCtrl",
        "eloue/controllers/bookings/BookingDetailCtrl",
        "eloue/controllers/DashboardLoginCtrl",
        "eloue/directives/FileChooserDirective",
        "../../common/eloue/controllers/AuthCtrl",
        "../../common/eloue/controllers/CookiesCtrl",
        "../../common/eloue/controllers/HeaderCtrl",
        "../../common/eloue/controllers/LoginCtrl",
        "../../common/eloue/controllers/RegisterCtrl",
        "../../common/eloue/controllers/ResetPasswordCtrl",
        "../../common/eloue/directives/Chosen",
        "../../common/eloue/directives/DashboardRedirect",
        "../../common/eloue/directives/Datepicker",
        "../../common/eloue/directives/DatepickerMonth",
        "../../common/eloue/directives/YearDatepicker",
        "../../common/eloue/directives/ExtendedDatepicker",
        "../../common/eloue/directives/FormFieldErrorManager",
        "../../common/eloue/directives/FormFieldMessage",
        "../../common/eloue/directives/FormMessage",
        "../../common/eloue/directives/LazyLoad",
        "../../common/eloue/directives/LoginForm",
        "../../common/eloue/directives/PasswordMatch",
        "../../common/eloue/directives/RegistrationForm",
        "../../common/eloue/directives/ResetPasswordForm",
        "../../common/eloue/directives/ScrollBottom",
        "../../common/eloue/directives/ZipcodeValidator",
        "../../common/eloue/interceptors/ErrorHandlerInterceptor"],
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
                    .state("messages.new", {
                        url: "/new_message/:bookingId",
                        templateUrl: "partials/dashboard/messages/message_detail.html",
                        controller: "NewMessageThreadCtrl"
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
                    .state("items.shipping", {
                        url: "/:id/shipping",
                        views: {
                            "": {
                                templateUrl: "partials/dashboard/items/item_detail.html"
                            },
                            "tabs@items.shipping": {
                                templateUrl: "partials/dashboard/items/tabs.html",
                                controller: "ItemsTabsCtrl"
                            },
                            "details@items.shipping": {
                                templateUrl: "partials/dashboard/items/shipping.html",
                                controller: "ItemsShippingCtrl"
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


                // push function to the interceptors which will intercept
                // the http responses of the whole application
                $httpProvider.interceptors.push("ErrorHandlerInterceptor");
            }
        ]);

        EloueApp.run(["$rootScope", "$http", "$state", "$window", "$document", "AuthService", function ($rootScope, $http, $state, $window, $document, AuthService) {
            $(".container-full-screen").show();
            AuthService.saveAttemptUrl($window.location.href);
            var i, c, navRoutes = ["dashboard", "messages", "bookings", "items", "account"], userToken = "",
                name = "user_token=", ca = $document[0].cookie.split(";");
            for (i = 0; i < ca.length; i += 1) {
                c = ca[i];
                while (c.charAt(0) === " ") {
                    c = c.substring(1);
                }
                if (c.indexOf(name) !== -1) {
                    userToken = c.substring(name.length, c.length);
                }
            }
            $http.defaults.useXDomain = true;
            delete $http.defaults.headers.common["X-Requested-With"];

            if (userToken && userToken.length > 0) {
                $http.defaults.headers.common.Authorization = "Bearer " + userToken;
            }

            var csrftoken = AuthService.getCSRFToken();
            if (csrftoken && csrftoken.length > 0) {
                $http.defaults.headers.common["X-CSRFToken"] = csrftoken;
            }

            // Route change event listener
            $rootScope.$on("$stateChangeStart",
                function (event, toState, toParams, fromState, fromParams) {
                    $rootScope.routeChangeInProgress = true;
                    if (!toState.insecure && !AuthService.isLoggedIn()) {
                        $rootScope.$broadcast("redirectToLogin");
                        event.preventDefault();
                    } else {
                        var stateName = toState.name;
                        angular.forEach(navRoutes, function (route) {
                            if (stateName.indexOf(route) === 0) {
                                $("[ui-sref='" + route + "']").addClass("current");
                            } else {
                                $("[ui-sref='" + route + "']").removeClass("current");
                            }
                        });
                    }
                });
            $rootScope.$on("$stateChangeSuccess",
                function (event, toState, toParams, fromState, fromParams) {
                    $rootScope.routeChangeInProgress = false;
                });

            $rootScope.$on("$stateChangeError",
                function (event, toState, toParams, fromState, fromParams, error) {
                    $rootScope.routeChangeInProgress = false;
                });

            /**
             * Catch "redirectToLogin" event
             */
            $rootScope.$on("redirectToLogin", function () {
                $state.go("login");
            });
        }]);
    });
