define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values", "../../../common/eloue/services/FormService"], function (EloueCommon) {
    "use strict";
    /**
     * Authentication service.
     */
    EloueCommon.factory("AuthService", [
        "$q", "$rootScope", "$window", "$document",
        "Endpoints", "AuthConstants", "RedirectAfterLogin", "Registration", "FormService",
        function ($q, $rootScope, $window, $document, Endpoints, AuthConstants, RedirectAfterLogin, Registration, FormService) {
            var authService = {};

            /**
             * Sign in user with provided credentials.
             * @param credentials user credentials
             * @returns Signed in user object
             * @param successCallback success callback function
             * @param errorCallback error callback function
             */
            authService.login = function (credentials, successCallback, errorCallback) {
                $.ajax({
                    url: Endpoints.oauth_url + "access_token/",
                    type: "POST",
                    data: {
                        client_id: AuthConstants.clientId,
                        client_secret: AuthConstants.clientSecret,
                        grant_type: AuthConstants.grantType,
                        username: credentials.username,
                        password: credentials.password
                    },
                    success: successCallback,
                    error: errorCallback
                });
            };

            /**
             * Sign in user after logging in Facebok account.
             * @param url login facebook url
             * @returns Signed in user object
             * @param successCallback success callback function
             * @param errorCallback error callback function
             */
            authService.loginFacebook = function (url, successCallback, errorCallback) {
                $.ajax({
                    url: url,
                    type: "GET",
                    success: successCallback,
                    error: errorCallback
                });
            };

            /**
             * Remove user token.
             */
            authService.clearUserData = function () {
                $document[0].cookie = "user_token=;expires=" + new Date(0).toGMTString() + ";path=/";
            };

            /**
             * Redirect to attempted URL.
             */
            authService.redirectToAttemptedUrl = function () {
                if ($window.location.href.indexOf("dashboard") !== -1) {
                    $window.location.href = RedirectAfterLogin.url;
                } else {
                    $rootScope.$broadcast("openModal", {
                        name: RedirectAfterLogin.url,
                        params: RedirectAfterLogin.params
                    });
                }
            };

            /**
             * Save URL that user attempts to access.
             */
            authService.saveAttemptUrl = function (name, params) {
                RedirectAfterLogin.url = name;
                RedirectAfterLogin.params = params;
            };

            /**
             * Sends password reset request.
             * @param form form
             * @param successCallback success callback
             * @param errorCallback error callback
             */
            authService.sendResetPasswordRequest = function (form, successCallback, errorCallback) {
                FormService.send("POST", "/reset/", form, successCallback, errorCallback);
            };

            /**
             * Sends password reset request.
             * @param form form
             * @param url post url
             * @param successCallback success callback
             * @param errorCallback error callback
             */
            authService.resetPassword = function (form, url, successCallback, errorCallback) {
                FormService.send("POST", url, form, successCallback, errorCallback);
            };

            /**
             * Register new account
             * @param account new account
             * @returns user promise object.
             */
            authService.register = function (account) {
                return Registration.register(account);
            };

            /**
             * Check if app user is logged in.
             * @returns true if user is logged in
             */
            authService.isLoggedIn = function () {
                return !!authService.getUserToken();
            };

            /**
             * Retrieves cookie value by provided cookie name.
             * @param cname cookie name
             */
            authService.getCookie = function getCookie(cname) {
                var name = cname + "=", ca = $document[0].cookie.split(";"), i, c;
                for (i = 0; i < ca.length; i += 1) {
                    c = ca[i];
                    while (c.charAt(0) === " ") {
                        c = c.substring(1);
                    }
                    if (c.indexOf(name) !== -1) {
                        return c.substring(name.length, c.length);
                    }
                }
                return null;
            };

            authService.getUserToken = function () {
                return authService.getCookie("user_token");
            };

            authService.getCSRFToken = function () {
                return authService.getCookie("csrftoken");
            };

            return authService;
        }]);
});
