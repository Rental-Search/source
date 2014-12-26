define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values", "../../../common/eloue/services/FormService"], function (EloueCommon) {
    "use strict";
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
                return Addresses.get({id: addressId, _cache: new Date().getTime()}).$promise;
            };

            addressesService.getAddressesByPatron = function (patronId) {
                var deferred = $q.defer();

                Addresses.get({patron: patronId, _cache: new Date().getTime()}).then(function (result) {
                    var total = result.count, pagesCount, adrPromises, i;
                    if (total <= 10) {
                        deferred.resolve(result.results);
                    } else {
                        pagesCount = Math.floor(total / 10) + 1;
                        adrPromises = [];

                        for (i = 1; i <= pagesCount; i += 1) {
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
                var deferred = $q.defer(),
                    currentAddressUrl = Endpoints.api_url + "addresses/" + addressId + "/";
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
                return Addresses.update({id: address.id}, address).$promise;
            };

            addressesService.saveAddress = function (address) {
                return Addresses.save(address).$promise;
            };

            addressesService.deleteAddress = function (addressId) {
                return Addresses.delete({id: addressId}).$promise;
            };

            return addressesService;
        }
    ]);
});
