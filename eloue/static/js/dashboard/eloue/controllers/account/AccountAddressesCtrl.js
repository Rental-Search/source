define([
    "eloue/app",
    "../../../../common/eloue/services/UsersService",
    "../../../../common/eloue/services/AddressesService"
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the account's addresses  page.
     */
    EloueDashboardApp.controller("AccountAddressesCtrl", [
        "$scope",
        "UsersService",
        "AddressesService",
        function ($scope, UsersService, AddressesService) {

            $scope.markListItemAsSelected("account-part-", "account.addresses");

            UsersService.getMe().then(function (currentUser) {
                var currentUserId = currentUser.id;

                AddressesService.getAddressesByPatron(currentUserId).then(function (results) {
                    $scope.addressList = results;
                    $scope.defaultAddressId = currentUser.default_address ? currentUser.default_address.id : null;
                });
            });
        }
    ]);
});
