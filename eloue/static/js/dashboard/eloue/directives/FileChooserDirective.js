"use strict";

define(["eloue/app"], function (EloueDashboardApp) {

    /**
     * Controller for the messages page.
     */
    EloueDashboardApp.directive("fileChooser", [function () {
        return {
            restrict: "A",
            scope: {
                onChange: "&"
            },
            link: function (scope, element, attrs) {
                element.bind("change", function () {
                    scope.onChange();
                });
            }
        };
    }]);
});
