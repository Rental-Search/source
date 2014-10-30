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
        "jquery-mousewheel",
        "custom-scrollbar",
        "jquery-autosize",
        "chosen",
        "../../common/eloue/commonApp"],
    function (angular) {
        // Create dashboard application
        return angular.module("EloueDashboardApp", ["EloueCommon", "ngCookies", "ngResource", "ngRoute", "ui.router",
            "pascalprecht.translate"]);
    }
);
