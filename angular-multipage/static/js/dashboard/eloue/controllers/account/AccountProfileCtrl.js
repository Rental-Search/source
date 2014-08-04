"use strict";

define(["angular", "eloue/app", "eloue/services/FormDataService"], function (angular) {

    /**
     * Controller for the account's profile page.
     */
    angular.module("EloueDashboardApp").controller("AccountProfileCtrl", ["$scope", "FormDataService", function ($scope, FormDataService) {
        $scope.title = "Profile title";

        $scope.submit = function () {
            var context = $("#profile_form");

            var texts = $(":text", context);
            var files = $(":file", context);

            FormDataService.send("/", texts, files, function () {
                // TODO onComplete
                console.log("TODO onComplete");
            });
        };
    }]);
});