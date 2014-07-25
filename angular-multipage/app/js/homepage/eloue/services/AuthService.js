define(["angular", "eloue/constants", "eloue/app"], function (angular) {
    "use strict";
    /**
     * Authentication service.
     */
    angular.module("EloueApp").factory("AuthService", ["$rootScope", "$location", "Endpoints", function ($rootScope, $location, Endpoints) {

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
                                window.alert("An error occured: " + jqXHR.responseJSON);
                            } else {
                                window.alert("An error occured!");
                            }
                        }
                    });
                } else {
                    self.authorize();
                }
            },

            authorize: function authorize() {
                var userToken = this.getCookie("user_token");
                if (userToken) {
                    $(".modal-backdrop").hide();
                    $location.path("/dashboard");
                }
            },

            /**
             * Check if app user is logged in.
             * @returns true if user is logged in
             */
            isLoggedIn: function () {
                var userToken = this.getCookie("user_token");
                return userToken;
            },

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