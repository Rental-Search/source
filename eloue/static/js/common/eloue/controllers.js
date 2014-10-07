"use strict";
define(["../../common/eloue/commonApp"], function (EloueCommon) {

    /**
     * Controller for the login form.
     */
    EloueCommon.controller("LoginCtrl", ["$scope", "$rootScope", "$http", "AuthService", "UsersService", "ServiceErrors", function ($scope, $rootScope, $http, AuthService, UsersService, ServiceErrors) {
        /**
         * User credentials.
         */
        $scope.credentials = {};

        $scope.loginError = null;

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
                + expire.toGMTString();
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
                });
                AuthService.redirectToAttemptedUrl();
            }
        }
    }]);

    /**
     * Controller for the reset password form.
     */
    EloueCommon.controller("ResetPasswordCtrl", ["$scope", "AuthService", "ServiceErrors", function ($scope, AuthService, ServiceErrors) {

        $scope.passwdResetStage = true;
        $scope.resetPasswordError = null;

        $scope.sendResetRequest = function() {
            var form = $("#reset-password-form");
            AuthService.sendResetPasswordRequest(
                form,
                function (data) {
                    $scope.onResetSuccess(data);
                },
                function (jqXHR) {
                    $scope.onResetError(jqXHR);
                });
        };

        $scope.onResetSuccess = function (data) {
            $scope.$apply(function () {
                $scope.passwdResetStage = false;
            });
        };

        $scope.onResetError = function (jqXHR) {
            var errorText = "";
            console.log(jqXHR);
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
    }]);

    /**
     * Controller for the registration form.
     */
    EloueCommon.controller("RegisterCtrl", ["$scope", "AuthService", "CivilityChoices", function ($scope, AuthService, CivilityChoices) {

        /**
         * New user account data.
         */
        $scope.account = {};

        /**
         * Error occurred during registration.
         */
        $scope.registrationError = null;
        $scope.civilityOptions = CivilityChoices;

        /**
         * Register new user in the system.
         */
        $scope.register = function register() {
            AuthService.register($scope.account).$promise.then(function (response) {
                // Sign in new user automatically
                var credentials = {
                    username: $scope.account.email,
                    password: $scope.account.password
                };
                AuthService.clearUserData();
                AuthService.login(credentials);
            }, function (error) {
                if (error.data && error.data.detail) {
                    $scope.$apply(function () {
                        $scope.registrationError = error.data.detail;
                    });
                }
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

        $("select").attr("eloue-chosen", "");
    }]);

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
                $window.location.reload();
            };
        }]);
});