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

            $scope.markListItemAsSelected("account-part-", "account.addresses");

            UsersService.getMe().$promise.then(function (currentUser) {
                var currentUserId = currentUser.id;

                AddressesService.getAddressesByPatron(currentUserId).then(function (results) {
                    $scope.addressList = results;
                    $scope.defaultAddressId = !!currentUser.default_address ? currentUser.default_address.id : null;
                });
            });
        }
    ]);
});