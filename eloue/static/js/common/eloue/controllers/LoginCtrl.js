define([
    "../../../common/eloue/commonApp",
    "../../../common/eloue/values",
    "../../../common/eloue/services/AuthService",
    "../../../common/eloue/services/UsersService",
    "../../../common/eloue/services/ToDashboardRedirectService"
], function (EloueCommon) {
    "use strict";
    /**
     * Controller for the login form.
     */
    EloueCommon.controller("LoginCtrl", [
        "$scope",
        "$rootScope",
        "$http",
        "$window",
        "AuthService",
        "UsersService",
        "ToDashboardRedirectService",
        "ServiceErrors",
        "RedirectAfterLogin",
        function ($scope, $rootScope, $http, $window, AuthService, UsersService, ToDashboardRedirectService, ServiceErrors, RedirectAfterLogin) {
            /**
             * User credentials.
             */
            $scope.credentials = {};

            $scope.loginError = null;

            $scope.emailPattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;

            $scope.inactiveUserError = null;

            $scope.activationLinkSentMsg = null;

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
                                $rootScope.$broadcast("loggedIn");
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
            $scope.login = function () {
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
                $rootScope.$broadcast("loggedIn");
            };

            $scope.onLoginError = function (jqXHR) {
                var errorText = "";
                if (jqXHR.status === 400) {
                    if (jqXHR.responseJSON.error == "user_inactive") {
                        $scope.$apply(function () {
                            $scope.inactiveUserError = "Cliquez ici pour recevoir le lien d'activation.";
                        });
                    }
                    if (ServiceErrors[jqXHR.responseJSON.error]) {
                        errorText = ServiceErrors[jqXHR.responseJSON.error];
                    } else {
                        errorText = "Bad request.";
                    }
                } else {
                    errorText = "An error occurred!";
                }
                $scope.$apply(function () {
                    $scope.loginError = errorText;
                });
            };

            /**
             * Send activation link to user email.
             */
            $scope.sendActivationLink = function() {
                AuthService.sendActivationLink($scope.credentials.username, $scope.onSendActivationLinkSuccess, $scope.onSendActivationLinkError);
            };

            $scope.onSendActivationLinkSuccess = function (data) {
                $scope.$apply(function () {
                    $scope.loginError = null;
                    $scope.inactiveUserError = null;
                    $scope.activationLinkSentMsg = data.detail;
                });
            };

            $scope.onSendActivationLinkError = function (jqXHR) {
                $scope.$apply(function () {
                    $scope.loginError = null;
                    $scope.inactiveUserError = null;
                    $scope.activationLinkSentMsg = jqXHR.responseJSON.error;
                });
            };

            /**
             * Authorize user by "user_token" cookie.
             */
            $scope.authorize = function () {
                var userToken = AuthService.getUserToken();
                if (userToken) {
                    $http.defaults.headers.common.authorization = "Bearer " + userToken;
                    $(".modal-backdrop").hide();
                    $(".modal").modal("hide");
                    UsersService.getMe(function (currentUser) {
                        // Save current user in the root scope
                        $rootScope.currentUser = currentUser;
                        if (RedirectAfterLogin.url !== "/") {
                            AuthService.redirectToAttemptedUrl();
                        } else {
                            $window.location.reload();
                        }
                    });
                }
            };
        }]);
});
