"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for redirection from Go Sport public page to e-loue dashboard app.
     */
    EloueCommon.factory("ToDashboardRedirectService", ["$window", "$cookies", function ($window, $cookies) {

        return {
            showPopupAndRedirect: function (href) {
                var delay,
                    modalView = $("#redirect"),
                    eloueRedirectUrl = $("#eloue_url_redirect"),
                    redirectResult;
                if (!modalView || modalView.length == 0) {
                    delay = 0;
                } else {
                    delay = 10000;
                    modalView.modal("show");
                }
                if (!eloueRedirectUrl || eloueRedirectUrl.length == 0) {
                    redirectResult = href;
                } else {
                    redirectResult = eloueRedirectUrl.val() + "?url=" + encodeURIComponent(href) + "&user_token=" + $cookies.user_token;
                }

                setTimeout(function () {
                    $window.location.href = redirectResult;
                }, delay);
            }
        };
    }]);
});
