define(["./../app"], function (app) {
    "use strict";
    /**
     * Authentication service.
     */
    app.factory("AuthService", ["$rootScope", "$cookieStore", "$location", function ($rootScope, $cookieStore, $location) {

        var user = $cookieStore.get("currentUser");

        return {


            /**
             * Sign in user with provided credentials.
             * @param credentials user credentials
             * @returns Signed in user object
             */
            login: function (credentials) {

            },

            /**
             * Sign out current user.
             */
            logout: function () {

            },

            /**
             * Check if app user is logged in.
             * @returns true if user is logged in
             */
            isLoggedIn: function () {
                return user && user.login != null;
            },

            /**
             * Check if app user is an admin.
             * @returns true for admin
             */
            isAdmin: function () {
                return user && user.isAdmin == true;
            },

            /**
             * Retrieve current user login.
             * @returns user login
             */
            getLogin: function () {
                return user ? user.login : "";
            }
        };
    }]);
});