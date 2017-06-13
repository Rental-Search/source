define(["eloue/app"], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the messages page.
     */
    EloueDashboardApp.directive("fileChooser", [function () {
        return {
            restrict: "A",
            scope: {
                onChange: "&"
            },
            link: function (scope, element) {
                element.bind("change", function () {
                    scope.onChange();
                });
            }
        };
    }]);
});
