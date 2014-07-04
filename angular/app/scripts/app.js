define(["angular", "controllers/MainCtrl", "controllers/LoginCtrl"], function (angular, MainCtrl, LoginCtrl) {
    "use strict";

    var eloueApp = angular.module("eloueApp", ["MainModule", "LoginModule",
        "ngCookies",
        "ngResource",
        "ngSanitize",
        "ngRoute"
    ]);
    eloueApp.config(function ($routeProvider) {
        $routeProvider
            .when("/", {
                templateUrl: "views/main.html",
                controller: "MainCtrl"
            })
            .otherwise({
                redirectTo: "/"
            });
    });
    return eloueApp;
});
