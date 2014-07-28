define(["angular", "eloue/app", "eloue/resources"], function (angular) {
    "use strict";
    /**
     * Product service.
     */
    angular.module("EloueApp").factory("ProductService", ["$q", "Products", "CheckAvailability", "Users", "Addresses", "PhoneNumbers", function ($q, Products, CheckAvailability, Users, Addresses, PhoneNumbers) {

        return {

            getProduct: function getProduct(id) {
                var deferred = $q.defer();
                var self = this;
                Products.get({id: id}).$promise.then(function (result) {
                    var promises = [];
                    //Get owner object
                    var ownerId = self.getIdFromUrl(result.owner);
                    promises.push(Users.get({id: ownerId}).$promise);
                    //Get address object
                    var addressId = self.getIdFromUrl(result.address);
                    promises.push(Addresses.get({id: addressId}).$promise);
                    //Get phone object
                    var phoneId = self.getIdFromUrl(result.phone);
                    promises.push(PhoneNumbers.get({id: phoneId}).$promise);

                    $q.all(promises).then(function success(results) {
                        result.owner = results[0];
                        result.address = results[1];
                        result.phone = results[2];
                        deferred.resolve(result);
                    });
                });
                return deferred.promise;
            },

            isAvailable: function isAvailable(id, startDate, endDate, quantity) {
                return CheckAvailability.get({id: id, started_at: startDate, ended_at: endDate, quantity: quantity});
            },

            getIdFromUrl: function getIdFromUrl(url) {
                var trimmedUrl = url.slice(0, url.length - 1);
                return trimmedUrl.substring(trimmedUrl.lastIndexOf("/") + 1, url.length);
            }
        };
    }]);
});