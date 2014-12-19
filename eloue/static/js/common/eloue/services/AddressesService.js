"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for managing addresses.
     */
    EloueCommon.factory("AddressesService", [
        "$q",
        "Addresses",
        "Endpoints",
        "FormService",
        function ($q, Addresses, Endpoints, FormService) {
            var addressesService = {};

            addressesService.getAddress = function (addressId) {
                return Addresses.get({id: addressId, _cache: new Date().getTime()});
            };

            addressesService.getAddressesByPatron = function (patronId) {
                var deferred = $q.defer();

                Addresses.get({patron: patronId, _cache: new Date().getTime()}).$promise.then(function (result) {
                    var total = result.count;
                    if (total <= 10) {
                        deferred.resolve(result.results);
                    } else {
                        var pagesCount = Math.floor(total / 10) + 1;
                        var adrPromises = [];

                        for (var i = 1; i <= pagesCount; i++) {
                            adrPromises.push(Addresses.get({
                                patron: patronId,
                                _cache: new Date().getTime(),
                                page: i
                            }).$promise);
                        }

                        $q.all(adrPromises).then(
                            function (addresses) {
                                var addressList = [];
                                angular.forEach(addresses, function (adrPage, index) {
                                    angular.forEach(adrPage.results, function (value, key) {
                                        addressList.push(value);
                                    });
                                });
                                deferred.resolve(addressList);
                            }
                        );

                    }
                });

                return deferred.promise;
            };

            addressesService.updateAddress = function (addressId, formData) {
                var deferred = $q.defer();

                var currentAddressUrl = Endpoints.api_url + "addresses/" + addressId + "/";
                FormService.send("POST", currentAddressUrl, formData,
                    function (data) {
                        deferred.resolve(data);
                    },
                    function (reason) {
                        deferred.reject(reason);
                    });

                return deferred.promise;
            };

            //TODO: leave only 1 update method for addresses
            addressesService.update = function (address) {
                return Addresses.update({id: address.id}, address);
            };

            addressesService.saveAddress = function (address) {
                return Addresses.save(address);
            };

            addressesService.deleteAddress = function (addressId) {
                return Addresses.delete({id: addressId});
            };

            return addressesService;
        }
    ]);
});
