define([
    "eloue/app",
    "../../../../common/eloue/values",
    "../../../../common/eloue/services/AddressesService",
    "../../../../common/eloue/services/ProductsService",
    "../../../../common/eloue/services/UsersService"
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the account's address detail page.
     */
    EloueDashboardApp.controller("AccountAddressDetailCtrl", [
        "$scope",
        "$state",
        "$stateParams",
        "Endpoints",
        "AddressesService",
        "ProductsService",
        "UsersService",
        function ($scope, $state, $stateParams, Endpoints, AddressesService, ProductsService, UsersService) {

            $scope.address = {};

            $scope.handleResponseErrors = function (error, object, action) {
                $scope.serverError = error.errors;
                $scope.submitInProgress = false;
                $scope.showNotification(object, action, false);
            };

            // Get
            AddressesService.getAddress($stateParams.id).then(function (address) {
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
                AddressesService.updateAddress($scope.address.id, form).then(
                    $scope.processAddressUpdateResponse,
                    function (error) {
                        $scope.handleResponseErrors(error, "address", "save");
                    }
                );
            };

            $scope.processAddressUpdateResponse = function () {
                if ($scope.defaultAddressId !== $stateParams.id) {
                    var userPatch = {};
                    userPatch.default_address = Endpoints.api_url + "addresses/" + $scope.address.id + "/";
                    UsersService.updateUser(userPatch).then(function (result) {
                        $scope.currentUser.default_address = result.default_addres;
                        $scope.finaliseAddressUpdate();
                    });
                } else {
                    $scope.finaliseAddressUpdate();
                }
            };

            $scope.finaliseAddressUpdate = function () {
                $scope.submitInProgress = false;
                $scope.showNotification("address", "save", true);
                $state.transitionTo($state.current, $stateParams, {reload: true});
            };

            // Delete address
            $scope.deleteAddress = function () {
                $scope.submitInProgress = true;
                AddressesService.deleteAddress($scope.address.id).then(function () {
                    $scope.submitInProgress = false;
                    $scope.showNotification("address", "delete", true);
                    $state.transitionTo("account.addresses", $stateParams, {reload: true});
                }, function (error) {
                    $scope.handleResponseErrors(error, "address", "delete");
                });
            };

            ProductsService.getProductsByAddress($stateParams.id).then(function (products) {
                $scope.productList = products;
            });

        }
    ]);
});
