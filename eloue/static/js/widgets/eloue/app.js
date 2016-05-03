define([
    "angular",
    "angular-cookie",
    "angular-cookies",
    "angular-resource",
    "angular-translate",
    "angular-i18n",
    "angularjs-slider",
    "js-cookie",
    "../../common/eloue/commonApp"
], function (angular) {
    "use strict";
    // Create application module
    return angular.module("EloueWidgetsApp", [
        "EloueCommon",
        "ngCookies",
        "ipCookie",
        "ngResource",
        "pascalprecht.translate",
        "algoliasearch",
        "rzModule",
        "uiGmapgoogle-maps"
    ]);
});
