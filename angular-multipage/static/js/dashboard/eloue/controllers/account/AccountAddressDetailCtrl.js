"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's address detail page.
     */
    angular.module("EloueDashboardApp").controller("AccountAddressDetailCtrl", [
        "$scope",
        "$stateParams",
        "AddressesService",
        "ProductsService",
        function ($scope, $stateParams, AddressesService, ProductsService) {
            AddressesService.getAddress($stateParams.id).$promise.then(function (address) {
                // List of addresses
                $scope.address = address;

                // Is this address default
                $scope.isDefaultAddress = address.id === $scope.defaultAddressId;

                // Submit form
                $scope.submitAddress = function () {
                    var form = $("#address_detail_form");
                    AddressesService.updateAddress($scope.address.id, form);
                };

                // Delete address
                $scope.deleteAddress = function () {
                    AddressesService.deleteAddress($scope.address.id);
                };
            });

            ProductsService.getProductsByAddress($stateParams.id).$promise.then(function (products) {
                $scope.productList = products.results;
                console.log($scope.productList);
            });
        }
    ]);
});