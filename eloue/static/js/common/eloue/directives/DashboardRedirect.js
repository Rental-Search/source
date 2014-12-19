"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * For redirect from Go Sport public part to E-loue dashbooard.
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
