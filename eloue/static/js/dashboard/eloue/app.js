define(["angular",
        "angular-cookie",
        "angular-cookies",
        "angular-resource",
        "angular-ui-router",
        "angular-translate",
        "angular-translate-interpolation-messageformat",
        "angular-moment",
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
        return angular.module("EloueDashboardApp", ["EloueCommon", "ngCookies", "ipCookie", "ngResource", "ui.router",
            "pascalprecht.translate", "angularMoment"]);
    });
