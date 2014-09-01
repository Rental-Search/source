define(["angular", "../../../../../common/eloue/values", "../../../../../common/eloue/resources", "eloue/modules/user_management/UserManagementModule"], function (angular) {
    "use strict";
    /**
     * Authentication service.
     */
    angular.module("EloueApp.UserManagementModule").factory("AuthService", ["$q", "$window", "Endpoints", "RedirectAfterLogin", "Registration", function ($q, $window, Endpoints, RedirectAfterLogin, Registration) {
        return {

            /**
             * Sign in user with provided credentials.
             * @param credentials user credentials
             * @returns Signed in user object
             */
            login: function (credentials) {
                var userToken = this.getCookie("user_token");
                var self = this;
                if (!userToken) {
                    $.ajax({
                        url: Endpoints.oauth_url + "access_token/",
                        type: "POST",
                        data: {
                            client_id: "51bcafe59e484b028657",
                            client_secret: "132a8a395c140e29f15c4341758c59faa33e012b",
                            grant_type: "password",
                            username: credentials.username,
                            password: credentials.password
                        },
                        success: function (data) {
                            var expire = new Date();
                            expire.setTime(new Date().getTime() + 3600000 * 24 * 30);
                            document.cookie = "user_token=" + escape(data.access_token) + ";expires="
                                + expire.toGMTString();
                            self.authorize();
                        },
                        error: function (jqXHR) {
                            if (jqXHR.status == 400) {
                                alert("An error occured: " + jqXHR.responseJSON);
                            } else {
                                alert("An error occured!");
                            }
                        }
                    });
                } else {
                    self.authorize();
                }
            },

            /**
             * Authorize user by "user_token" cookie.
             */
            authorize: function () {
                var userToken = this.getCookie("user_token");
                if (userToken) {
                    $(".modal-backdrop").hide();
                    this.redirectToAttemptedUrl();
                }
            },

            /**
             * Remove user token.
             */
            clearUserData: function () {
                document.cookie = "user_token=;expires=" + new Date(0).toGMTString();
            },

            /**
             * Redirect to attempted URL.
             */
            redirectToAttemptedUrl: function() {
                $window.location.href = RedirectAfterLogin.url;
            },

            /**
             * Save URL that user attempts to access.
             */
            saveAttemptUrl: function() {
                RedirectAfterLogin.url = $window.location.href;
            },

            /**
             * Register new account
             * @param account new account
             * @returns user promise object.
             */
            register: function (account) {
                return Registration.register(account);
            },

            /**
             * Check if app user is logged in.
             * @returns true if user is logged in
             */
            isLoggedIn: function () {
                return this.getCookie("user_token");
            },

            /**
             * Retrieves cookie value by provided cookie name.
             * @param cname cookie name
             */
            getCookie: function getCookie(cname) {
                var name = cname + "=";
                var ca = document.cookie.split(';');
                for (var i = 0; i < ca.length; i++) {
                    var c = ca[i];
                    while (c.charAt(0) == ' ') c = c.substring(1);
                    if (c.indexOf(name) != -1) return c.substring(name.length, c.length);
                }
                return "";
            }
        };
    }]);
});