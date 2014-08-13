"use strict";
define(["angular",
        "angular-cookies",
        "angular-resource",
        "angular-route",
        "angular-ui-router",
        "jquery-form",
        "selectivizr",
        "custom-scrollbar",
        "jquery-autosize",
        "jquery-chosen",
        "dashboard_scripts",
        "bootstrap_modal",
        "../../common/eloue/commonApp"],
    function (angular) {
        // Create dashboard application
        return angular.module("EloueDashboardApp", ["EloueCommon", "ngCookies", "ngResource", "ngRoute", "ui.router"]);
    }
);