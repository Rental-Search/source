"use strict";
define(["angular",
        "angular-cookies",
        "angular-resource",
        "angular-route",
        "angular-ui-router",
        "angular-translate",
        "toastr",
        "formmapper",
        "jquery-form",
        "selectivizr",
        "custom-scrollbar",
        "jquery-autosize",
        "jquery-chosen",
        "../../common/eloue/commonApp"],
    function (angular) {
        // Create dashboard application
        return angular.module("EloueDashboardApp", ["EloueCommon", "ngCookies", "ngResource", "ngRoute", "ui.router",
            "pascalprecht.translate"]);
    }
);