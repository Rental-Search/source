"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Modifies component representation using Chosen.js
     */
    EloueCommon.directive("eloueChosen", ["$timeout", function ($timeout) {
        return {
            restrict: "A",
            link: function (scope, element, attrs) {

                scope.$watch(attrs.chosen, function () {
                    element.trigger("chosen:updated");
                });

                scope.$watch(attrs.ngModel, function () {
                    element.trigger("chosen:updated");
                });

                scope.$watch(attrs.opts, function () {
                    $timeout(function () {
                        element.trigger("chosen:updated");
                    }, 300);
                });

                element.chosen();
            }
        };
    }]);
});
