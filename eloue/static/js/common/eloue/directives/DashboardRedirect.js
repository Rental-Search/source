define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    "use strict";
    /**
     * For redirect from Go Sport public part to E-loue dashboard.
     */
    EloueCommon.directive("eloueDashboardRedirect", ["ToDashboardRedirectService", function (ToDashboardRedirectService) {
        return {
            restrict: "A",
            link: function (scope, element, attrs) {
                var href = attrs.eloueDashboardRedirect;
                element.on("click", function (event) {
                    event.preventDefault();

                    ToDashboardRedirectService.showPopupAndRedirect(href);

                });
            }
        };
    }]);
});
