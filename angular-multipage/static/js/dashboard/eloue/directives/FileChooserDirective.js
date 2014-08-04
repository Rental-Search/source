"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the messages page.
     */
    angular.module("EloueDashboardApp").directive("fileChooser", ["FileReader", "$parse",
        function (FileReader, $parse) {
            return {
                restrict: "A",
                link: function (scope, element, attrs) {
                    var urlModel = $parse(attrs.urlModel);
                    
                    element.bind("change", function () {
                        FileReader.readAsDataUrl(element[0].files[0], scope).then(function (result) {
                            urlModel.assign(scope, result)
                        });
                    });
                }
            };
        }
    ]);
});