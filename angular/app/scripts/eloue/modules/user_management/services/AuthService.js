define(["angular", "eloue/constants", "eloue/modules/user_management/UserManagementModule"], function (angular) {
    "use strict";
    /**
     * Authentication service.
     */
    angular.module("EloueApp.UserManagementModule").factory("AuthService", ["$rootScope", "$cookieStore", "$location", "Endpoints", function ($rootScope, $cookieStore, $location, Endpoints) {

        return {


            /**
             * Sign in user with provided credentials.
             * @param credentials user credentials
             * @returns Signed in user object
             */
            login: function (credentials) {
                var userToken = $cookieStore.get("user_token");
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
                            console.log(data.access_token);
                            $cookieStore.put("user_token", data.access_token);
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
                var userToken = $cookieStore.get("user_token");
                if (userToken) {
                    $(".modal-backdrop").hide();
                    $location.path("/dashboard");
//                    $.ajax({
//                        url: Endpoints.api_url + "users/",
//                        type: "POST",
//                        headers: {
//                            Authorization: "Bearer " + userToken
//                        },
//                        data: {},
//                        success: function (data) {
//                            console.log(data);
//
//                        },
//                        error: function (jqXHR) {
//                            if (jqXHR.status == 400) {
//                                window.alert("An error occured: " + jqXHR.responseJSON);
//                            } else {
//                                window.alert("An error occured!");
//                            }
//                        }
//                    });
                }
            },

            /**
             * Check if app user is logged in.
             * @returns true if user is logged in
             */
            isLoggedIn: function () {
                var userToken = $cookieStore.get("user_token");
                return userToken;
            }
        };
    }]);
});