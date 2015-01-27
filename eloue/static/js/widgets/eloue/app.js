define([
    "angular",
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
        "ngResource",
        "pascalprecht.translate"
    ]);
});
