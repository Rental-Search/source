"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the messages page.
     */
    angular.module("EloueDashboardApp").factory("FormDataService", [function () {
        var formDataService = {};

        formDataService.send = function (action, texts, files, onComplete) {
            $.ajax(action, {
                data: texts.serializeArray(),
                files: files,
                iframe: true,
                processData: false
            }).complete(function(data) {
                if (!!onComplete) {
                    onComplete(data);
                }
            });
        };

        return formDataService;
    }]);
});