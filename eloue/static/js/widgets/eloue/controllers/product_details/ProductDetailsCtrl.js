define([
    "eloue/app"
], function (EloueWidgetsApp) {
    "use strict";

    EloueWidgetsApp.controller("ProductDetailsCtrl", [
        "$scope",
        function ($scope) {
            /**
             * Select tab in main product detail page content part.
             */
            $scope.selectTab = function (tabName) {
                $("[id^=tabs-]").each(function () {
                    var item = $(this);
                    if (("#" + item.attr("id")) == tabName) {
                        item.removeClass("ng-hide");
                    } else {
                        item.addClass("ng-hide");
                    }
                });
                $("a[href^=#tabs-]").each(function () {
                    var item = $(this);
                    if (item.attr("href") == tabName) {
                        item.addClass("current");
                    } else {
                        item.removeClass("current");
                    }
                });
            };

            $scope.selectTab("#tabs-photos");
        }]);
});
