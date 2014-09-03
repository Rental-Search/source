"use strict";
define(["../../common/eloue/commonApp"], function (EloueCommon) {

    /**
     * Controller for the login form.
     */
    EloueCommon.controller("LoginCtrl", ["$scope", "$cookies", "AuthService", function ($scope, $cookies, AuthService) {
        /**
         * User credentials.
         */
        $scope.credentials = {};

        $scope.loginError = "";

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

            if (jqXHR.status == 400) {
                $scope.loginError = "An error occured: " + jqXHR.responseJSON;
                console.log($scope.loginError);
            } else {
                $scope.loginError = "An error occured!";
            }
        };

        /**
         * Authorize user by "user_token" cookie.
         */
        $scope.authorize = function () {
            var userToken = $cookies.user_token;
            if (userToken) {
                $(".modal-backdrop").hide();
                //TODO: redirect
//                this.redirectToAttemptedUrl();
            }
        }
    }]);

    /**
     * Controller for the registration form.
     */
    EloueCommon.controller("RegisterCtrl", ["$scope", "AuthService", function ($scope, AuthService) {

        /**
         * New user account data.
         */
        $scope.account = {};

        /**
         * Error occurred during registration.
         */
        $scope.registrationError = "";

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
                $scope.registrationError = error.data.detail;
            });
        };

        /**
         * Opens registration via email form.
         */
        $scope.openRegistrationForm = function openRegistrationForm() {
            var classic_form = $('.classic-form');
            classic_form.slideDown();
            $('.registration.email').slideUp();
        }
    }]);
});