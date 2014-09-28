"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the messages page.
     */
    angular.module("EloueDashboardApp").directive("fileChooser", [function () {
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