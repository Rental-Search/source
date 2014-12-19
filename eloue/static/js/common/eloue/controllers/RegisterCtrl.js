"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
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
            if ($scope.account.confirmPassword !== $scope.account.password) {
                ServerValidationService.removeErrors();
                ServerValidationService.addError("confirmPassword", "Passwords not match");
            } else {
                $scope.submitting = true;
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
                            $scope.submitting = false;
                        },
                        function (jqXHR) {
                            $scope.onLoginError(jqXHR);
                            $scope.submitting = false;
                        }
                    );
                }, function (error) {
                    $scope.submitting = false;
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
            }
            if (url.indexOf("message") > 0) {
                return "Message";
            }
            if (url.indexOf("phone") > 0) {
                return "Appel";
            }
            if (url.indexOf("publish") > 0) {
                return "Dépôt annonce";
            }
            return "Simple";
        };

        /**
         * Sign in user with facebook.
         */
        $scope.loginFacebook = function () {
            FB.login(function (response) {
                if (!!response.authResponse) {
                    AuthService.loginFacebook(
                        $("#eloue_url_redirect_facebook").val() + "?access_token=" + response.authResponse.accessToken + "&user_id=" + response.authResponse.userID + "&expires_in=" + response.authResponse.expiresIn + "&create_user=true",
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
         * Opens registration via email form.
         */
        $scope.openRegistrationForm = function openRegistrationForm() {
            var classicForm = $(".classic-form");
            classicForm.slideDown();
            $(".registration.email").slideUp();
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
        $scope.trackEvent = function (category, action, value) {
            _gaq.push(["_trackEvent", category, action, value]);
        };

        /**
         * Push track page view to Google Analytics.
         */
        $scope.trackPageView = function () {
            _gaq.push(["_trackPageview", $window.location.href + "/success/"]);
        };

        $("select").attr("eloue-chosen", "");
    }]);
});
