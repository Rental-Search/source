"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Controller for the login form.
     */
    EloueCommon.controller("LoginCtrl", ["$scope", "$rootScope", "$http", "$window", "AuthService", "UsersService", "ToDashboardRedirectService", "ServiceErrors", "RedirectAfterLogin", function ($scope, $rootScope, $http, $window, AuthService, UsersService, ToDashboardRedirectService, ServiceErrors, RedirectAfterLogin) {
        /**
         * User credentials.
         */
        $scope.credentials = {};

        $scope.loginError = null;

        $scope.emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;

        /**
         * Sign in user with facebook.
         */
        $scope.loginFacebook = function () {
            FB.login(function (response) {
                if (!!response.authResponse) {
                    AuthService.loginFacebook(
                        $("#eloue_url_redirect_facebook").val() + "?access_token=" + response.authResponse.accessToken + "&user_id=" + response.authResponse.userID + "&expires_in=" + response.authResponse.expiresIn,
                        function (data) {
                            $scope.authorize();
                            $scope.submitting = false;
                        },
                        function (jqXHR) {
                            $scope.onLoginError(jqXHR);
                            $scope.submitting = false;
                        }
                    );
                }
            }, {scope: "public_profile, email"});
        };

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
            document.cookie = "user_token=" + encodeURIComponent(data.access_token) + ";expires=" +
            expire.toGMTString() + ";path=/";
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
                $(".modal").modal("hide");
                UsersService.getMe(function (currentUser) {
                    // Save current user in the root scope
                    $rootScope.currentUser = currentUser;
                    if (RedirectAfterLogin.url != "/") {
                        AuthService.redirectToAttemptedUrl();
                    } else {
                        $window.location.reload();
                    }
                });
            }
        };
    }]);
});
