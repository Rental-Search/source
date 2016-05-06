define([
    "../../../common/eloue/commonApp",
    "../../../common/eloue/values",
    "../../../common/eloue/services/AuthService",
    "../../../common/eloue/services/UsersService",
    "../../../common/eloue/services/ToDashboardRedirectService",
    "../../../common/eloue/services/ServerValidationService"
], function (EloueCommon) {
    "use strict";
    /**
     * Controller for the registration form.
     */
    EloueCommon.controller("RegisterCtrl", [
        "$scope", "$rootScope", "$http", "$window", "$document", "$translate",
        "AuthService",
        "CivilityChoices",
        "UsersService",
        "ServiceErrors",
        "RedirectAfterLogin",
        "ToDashboardRedirectService",
        "ServerValidationService",
        function ($scope, $rootScope, $http, $window, $document, $translate, AuthService, CivilityChoices, UsersService, ServiceErrors, RedirectAfterLogin, ToDashboardRedirectService, ServerValidationService) {

            /**
             * New user account data.
             */
            $scope.account = {};

            $scope.civilityOptions = CivilityChoices[$translate.use()];

            /**
             * Register new user in the system.
             */
            $scope.register = function register() {
                if ($scope.account.confirmPassword !== $scope.account.password) {
                    ServerValidationService.removeErrors();
                    ServerValidationService.addError("confirmPassword", "Passwords not match");
                } else {
                    $scope.submitting = true;
                    AuthService.register($scope.account).then(function () {
                        $scope.trackEvent("Membre", "Inscription", $scope.getEventLabel());
                        $scope.trackPageView();
                        // Sign in new user automatically
                        var credentials = {
                            username: $scope.account.email,
                            password: $scope.account.password
                        };
                        AuthService.clearUserData();
                        AuthService.login(
                            credentials,
                            function (data) {
                                $scope.onLoginSuccess(data);
                                $scope.submitting = false;
                            },
                            function (jqXHR) {
                                $scope.onLoginError(jqXHR);
                                $scope.submitting = false;
                            }
                        );
                    }, function () {
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
                    if (response.authResponse) {
                        AuthService.loginFacebook(
                            $("#eloue_url_redirect_facebook").val() + "?access_token=" + response.authResponse.accessToken + "&user_id=" + response.authResponse.userID + "&expires_in=" + response.authResponse.expiresIn + "&create_user=true",
                            function () {
                                $scope.authorize('facebook');
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
                $document[0].cookie = "user_token=" + encodeURIComponent(data.access_token) + ";expires=" +
                    expire.toGMTString() + ";path=/";
                $scope.authorize('form');
            };

            $scope.onLoginError = function (jqXHR) {
                var errorText = "";
                if (jqXHR.status === 400) {
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
             * Opens registration via email form.
             */
            $scope.openRegistrationForm = function openRegistrationForm() {
                var classicForm = $(".classic-form");
                classicForm.slideDown();
                $(".registration.email").slideUp();
            };

            /**
             * Authorize user by "user_token" cookie.
             * @param support facebook or form
             */
            $scope.authorize = function (support) {
                var userToken = AuthService.getUserToken();
                if (userToken) {
                    $http.defaults.headers.common.authorization = "Bearer " + userToken;
                    $(".modal-backdrop").hide();
                    $(".modal").modal("hide");
                    UsersService.getMe(function (currentUser) {
                        // Save current user in the root scope
                        $rootScope.currentUser = currentUser;
                        $scope.segmentTrackEvent(support);
                        if (RedirectAfterLogin.url !== "/") {
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

            /**
             * Push track event to segment.
             *
             * @param support of the sign up type (facebook or form)
             */
            $scope.segmentTrackEvent = function (support) {
                analytics.alias($rootScope.currentUser.id);
                analytics.identify($rootScope.currentUser.id, {
                    'createdAt': $rootScope.currentUser.date_joined,
                    'email': $rootScope.currentUser.email,
                    'firstName': $rootScope.currentUser.first_name,
                    'lastName': $rootScope.currentUser.last_name,
                    'name': $rootScope.currentUser.first_name + " " + $rootScope.currentUser.last_name,
                    'username': $rootScope.currentUser.username,
                    'newsletter': $rootScope.currentUser.is_subscribed,
                    'last login': new Date()
                });
                analytics.track('Signed Up', {
                    'support': support,
                    'email': $rootScope.currentUser.email
                });
            };
        }]);
});
