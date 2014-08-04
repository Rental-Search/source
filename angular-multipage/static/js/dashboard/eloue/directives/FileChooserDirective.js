"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the messages page.
     */
    angular.module("EloueDashboardApp").directive("fileChooser", ["FileReader", function (FileReader) {
        return {
            restrict: "A",
            link: function (scope, element, attrs) {
                element.bind("change", function () {
                    var urlModel = attrs.urlModel;

                    FileReader.readAsDataUrl(element[0].files[0], scope).then(function (result) {
                        scope[urlModel] = result;
                    });
                });
            }
        };
    }]);
});