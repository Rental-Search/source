define([
    "angular",
    "angular-cookie",
    "angular-cookies",
    "angular-resource",
    "angular-translate",
    "angular-i18n",
    "../../common/eloue/commonApp"
], function (angular) {
    "use strict";
    // Create application module
    return angular.module("EloueWidgetsApp", [
        "EloueCommon",
        "ngCookies",
        "ipCookie",
        "ngResource",
        "pascalprecht.translate"
    ]);
});
