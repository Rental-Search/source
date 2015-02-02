define(["angular",
        "angular-cookies",
        "angular-resource",
        "angular-ui-router",
        "angular-translate",
        "toastr",
        "formmapper",
        "filesaver",
        "jquery-form",
        "selectivizr",
        "jquery-mousewheel",
        "custom-scrollbar",
        "jquery-autosize",
        "chosen",
        "../../common/eloue/commonApp"],
    function (angular) {
        "use strict";
        // Create dashboard application
        return angular.module("EloueDashboardApp", ["EloueCommon", "ngCookies", "ngResource", "ui.router",
            "pascalprecht.translate"]);
    });
