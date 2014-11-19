"use strict";
define(["../../common/eloue/commonApp"], function (EloueCommon) {

    /**
     * Controller for the login form.
     */
    EloueCommon.controller("LoginCtrl", ["$scope", "$rootScope", "$http", "$window", "AuthService", "UsersService", "ServiceErrors", function ($scope, $rootScope, $http, $window, AuthService, UsersService, ServiceErrors) {
        /**
         * User credentials.
         */
        $scope.credentials = {};

        $scope.loginError = null;

        $scope.emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;

        /**
         * Sign in user.
         */
        $scope.login = function login() {
            AuthService.login(
                $scope.credentials,


                function (data) {
                    $scope.onLoginSuccess(data);
                },
                function (jqXHR) {
                    $scope.onLoginError(jqXHR);
                }
            );
        };

        $scope.onLoginSuccess = function (data) {
            var expire = new Date();
            expire.setTime(new Date().getTime() + 3600000 * 24 * 30);
            document.cookie = "user_token=" + escape(data.access_token) + ";expires="
                + expire.toGMTString() + ";path=/";
            $scope.authorize();
        };

        $scope.onLoginError = function (jqXHR) {
            var errorText = "";
            if (jqXHR.status == 400) {
                if (!!ServiceErrors[jqXHR.responseJSON.error]) {
                    errorText = ServiceErrors[jqXHR.responseJSON.error];
                } else {
                    errorText = "Bad request.";
                }
            } else {
                errorText = "An error occured!";
            }
            $scope.$apply(function () {
                $scope.loginError = errorText;
            });
        };

        /**
         * Authorize user by "user_token" cookie.
         */
        $scope.authorize = function () {
            var userToken = AuthService.getCookie("user_token");
            if (!!userToken) {
                $http.defaults.headers.common.authorization = "Bearer " + userToken;
                $(".modal-backdrop").hide();
                $('.modal').modal('hide');
                UsersService.getMe(function (currentUser) {
                    // Save current user in the root scope
                    $rootScope.currentUser = currentUser;
                    //AuthService.redirectToAttemptedUrl();
                    if($window.location.href.indexOf("dashboard") !== -1) {
                        $window.location.href = "/dashboard";
                    }else{
                        $window.location.reload();
                    }
                });
            }
        }
    }]);

    /**
     * Controller for the reset password form.
     */
    EloueCommon.controller("ResetPasswordCtrl", ["$scope", "$window", "AuthService", "ServiceErrors", function ($scope, $window, AuthService, ServiceErrors) {

        $scope.passwdResetStage = true;
        $scope.passwdResetSuccess = false;
        $scope.resetPasswordError = null;

        $scope.sendResetRequest = function() {
            var form = $("#request-reset-password-form");
            AuthService.sendResetPasswordRequest(
                form,
                function (data) {
                    $scope.onSendResetRequestSuccess(data);
                },
                function (jqXHR) {
                    $scope.onSendResetRequestError(jqXHR);
                });
        };

        $scope.onSendResetRequestSuccess = function (data) {
            $scope.$apply(function () {
                $scope.passwdResetStage = false;
            });
        };

        $scope.onSendResetRequestError = function (jqXHR) {
            var errorText = "";
            if (jqXHR.status == 400) {
                if (!!jqXHR.responseJSON.errors.email) {
                    errorText = jqXHR.responseJSON.errors.email[0];
                } else {
                    errorText = "Bad request.";
                }
            } else {
                errorText = "An error occured!";
            }
            $scope.$apply(function () {
                $scope.resetPasswordError = errorText;
            });
        };

        $scope.resetPassword = function() {
            var form = $("#reset-password-form");
            AuthService.resetPassword(
                form,
                $window.location,
                function (data) {
                    $scope.onResetPasswordSuccess(data);
                },
                function (jqXHR) {
                    $scope.onResetPasswordError(jqXHR);
                });
        };

        $scope.onResetPasswordSuccess = function (data) {
            $scope.$apply(function () {
                $scope.passwdResetSuccess = true;
            });
        };

        $scope.onResetPasswordError = function (jqXHR) {
            var errorText = "";
            if (jqXHR.status == 400) {
                console.log(jqXHR.responseJSON);
                if (!!jqXHR.responseJSON.errors.__all__) {
                    errorText = jqXHR.responseJSON.errors.__all__[0];
                } else {
                    errorText = "Bad request.";
                }
            } else {
                errorText = "An error occured!";
            }
            $scope.$apply(function () {
                $scope.resetPasswordError = errorText;
            });
        };

        $("#reset-password-confirm").modal("show");
    }]);

    /**
     * Controller for the registration form.
     */
    EloueCommon.controller("RegisterCtrl", ["$scope", "$rootScope", "$http", "$window", "AuthService", "CivilityChoices", "UsersService", "ServiceErrors", "RedirectAfterLogin", "ToDashboardRedirectService", "ServerValidationService", function ($scope, $rootScope, $http, $window, AuthService, CivilityChoices, UsersService, ServiceErrors, RedirectAfterLogin, ToDashboardRedirectService, ServerValidationService) {

        /**
         * New user account data.
         */
        $scope.account = {};

        $scope.civilityOptions = CivilityChoices;

        /**
         * Register new user in the system.
         */
        $scope.register = function register() {
            if($scope.account.confirmPassword !== $scope.account.password){
                ServerValidationService.removeErrors();
                ServerValidationService.addError("confirmPassword", "Passwords not match");
            } else {
                AuthService.register($scope.account).$promise.then(function (response) {
                    $scope.trackEvent("Membre", "Inscription", $scope.getEventLabel());
                    $scope.trackPageView();
                    // Sign in new user automatically
                    var credentials = {
                        username: $scope.account.email,
                        password: $scope.account.password
                    };
                    AuthService.clearUserData();
                    AuthService.login(credentials,
                        function (data) {
                            $scope.onLoginSuccess(data);
                        },
                        function (jqXHR) {
                            $scope.onLoginError(jqXHR);
                        }
                    );
                }, function (error) {

                });
            }
        };

        /**
         * Get label for google analytics event base on product category.
         * @returns event tag label
         */
        $scope.getEventLabel = function () {
            var url = RedirectAfterLogin.url;
            if (url.indexOf("booking") > 0) {
                return "Réservation";
            } else if (url.indexOf("message") > 0) {
                return "Message";
            } else if (url.indexOf("phone") > 0) {
                return "Appel";
            } else if (url.indexOf("publish") > 0) {
                return "Dépôt annonce";
            } else {
                return "Simple";
            }
        };

        $scope.onLoginSuccess = function (data) {
            var expire = new Date();
            expire.setTime(new Date().getTime() + 3600000 * 24 * 30);
            document.cookie = "user_token=" + escape(data.access_token) + ";expires="
                + expire.toGMTString() + ";path=/";
            $scope.authorize();
        };

        $scope.onLoginError = function (jqXHR) {
            var errorText = "";
            if (jqXHR.status == 400) {
                if (!!ServiceErrors[jqXHR.responseJSON.error]) {
                    errorText = ServiceErrors[jqXHR.responseJSON.error];
                } else {
                    errorText = "Bad request.";
                }
            } else {
                errorText = "An error occured!";
            }
            $scope.$apply(function () {
                $scope.loginError = errorText;
            });
        };

        /**
         * Opens registration via email form.
         */
        $scope.openRegistrationForm = function openRegistrationForm() {
            var classic_form = $('.classic-form');
            classic_form.slideDown();
            $('.registration.email').slideUp();
        };

        /**
         * Authorize user by "user_token" cookie.
         */
        $scope.authorize = function () {
            var userToken = AuthService.getCookie("user_token");
            if (!!userToken) {
                $http.defaults.headers.common.authorization = "Bearer " + userToken;
                $(".modal-backdrop").hide();
                $('.modal').modal('hide');
                UsersService.getMe(function (currentUser) {
                    // Save current user in the root scope
                    $rootScope.currentUser = currentUser;
                    if (RedirectAfterLogin.url != "/") {
                        AuthService.redirectToAttemptedUrl();
                    } else {
                        //$window.location.href = "/dashboard"
                        ToDashboardRedirectService.showPopupAndRedirect("/dashboard");
                    }
                });
            }
        };

        /**
         * Push track event to Google Analytics.
         *
         * @param category category
         * @param action action
         * @param value value
         */
        $scope.trackEvent = function(category, action, value) {
            _gaq.push(["_trackEvent", category, action, value]);
        };

        /**
         * Push track page view to Google Analytics.
         */
        $scope.trackPageView = function() {
            _gaq.push(["_trackPageview", $window.location.href + "/success/"]);
        };

        $("select").attr("eloue-chosen", "");
    }]);

    /**
     * Controller handles modal window open/close event, checks user authentication and triggers specific handlers in controllers depend on scope.
     */
    EloueCommon.controller("ModalCtrl", [
        "$scope",
        "$rootScope",
        "$route",
        "$location",
        "$timeout",
        "AuthService",
        function($scope, $rootScope, $route, $location, $timeout, AuthService) {
            var currentUserToken = AuthService.getCookie("user_token");
            var currentRoute = $route.current.$$route;
            var path =  $route.current.$$route.originalPath;
            var prefix =path.slice(1,path.length);
            if (prefix != "login") {
                AuthService.saveAttemptUrl();
            }
            if (!!currentRoute.secure && !currentUserToken) {
                $location.path("/login");
            } else {
                $rootScope.$broadcast("openModal", { name : prefix, params: $route.current.params});
                $(".modal").modal("hide");
                $timeout(function() {
                    var modalContainer = $("#" + prefix + "Modal");
                    modalContainer.modal("show");
                    modalContainer.on( "hidden.bs.modal", function() {
                        $rootScope.$broadcast("closeModal", { name : prefix, params: $route.current.params});
                    });
                }, 300);
            }
        }]);

    /**
     * Root controller for pages which content depends on user authorized (e.g. Home page).
     */
    EloueCommon.controller("AuthCtrl", [
        "$scope",
        "$window",
        "AuthService",
        "UsersService",
        function($scope, $window, AuthService, UsersService) {
            var currentUserToken = AuthService.getCookie("user_token");
            if (currentUserToken) {
                // Get current user
                $scope.currentUserPromise = UsersService.getMe().$promise;
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    UsersService.getStatistics($scope.currentUser.id).$promise.then(function (stats) {
                        $scope.userStats = stats;
                    });
                });
            }

            $scope.logout = function() {
                AuthService.clearUserData();
                $window.location.href = "/";
            };
        }]);
});