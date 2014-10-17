"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's address detail page.
     */
    angular.module("EloueDashboardApp").controller("AccountAddressDetailCtrl", [
        "$scope",
        "$state",
        "$stateParams",
        "AddressesService",
        "ProductsService",
        function ($scope, $state, $stateParams, AddressesService, ProductsService) {

            $scope.address = {};

            // Get
            AddressesService.getAddress($stateParams.id).$promise.then(function (address) {
                // Current address
                $scope.address = address;
                $scope.markListItemAsSelected("account-address-", $stateParams.id);
                // Is this address default
                $scope.isDefaultAddress = address.id === $scope.defaultAddressId;
            });

            // Submit form
            $scope.submitAddress = function () {
                $scope.submitInProgress = true;
                var form = $("#address_detail_form");
                AddressesService.updateAddress($scope.address.id, form).then(function(result) {
                    $scope.submitInProgress = false;
                    $scope.showNotification("Adresse enregistrée");
                    $state.transitionTo($state.current, $stateParams, { reload: true });
                });
            };

            // Delete address
            $scope.deleteAddress = function () {
                $scope.submitInProgress = true;
                AddressesService.deleteAddress($scope.address.id).$promise.then(function(result) {
                    $scope.submitInProgress = false;
                    $scope.showNotification("Adresse supprimée");
                    $state.transitionTo("account.addresses", $stateParams, { reload: true });
                });
            };

            ProductsService.getProductsByAddress($stateParams.id).then(function (products) {
                $scope.productList = products;
            });
        }
    ]);
});