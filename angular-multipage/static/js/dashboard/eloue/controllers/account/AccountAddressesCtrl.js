"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's addresses  page.
     */
    angular.module("EloueDashboardApp").controller("AccountAddressesCtrl", [
        "$scope",
        "UsersService",
        "AddressesService",
        "UtilsService",
        function ($scope, UsersService, AddressesService, UtilsService) {
            UsersService.getMe().$promise.then(function (currentUser) {
                var currentUserId = currentUser.id;

                AddressesService.getAddressesByPatron(currentUserId).$promise.then(function (data) {
                    $scope.addressList = data.results;
                    $scope.defaultAddressId = UtilsService.getIdFromUrl(currentUser.default_address);
                    console.log(data.results);
                });
            });
        }
    ]);
});