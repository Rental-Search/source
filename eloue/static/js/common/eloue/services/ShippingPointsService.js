"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for managing shipping points.
     */
    EloueCommon.factory("ShippingPointsService", [
        "ShippingPoints",
        "Products",
        function (ShippingPoints, Products) {
            var shippingPointsService = {};

            shippingPointsService.searchDepartureShippingPointsByAddress = function (address) {
                return shippingPointsService.searchShippingPointsByAddress(address, 1);
            };

            shippingPointsService.searchDepartureShippingPointsByCoordinates = function (lat, lng) {
                return shippingPointsService.searchShippingPointsByCoordinates(lat, lng, 1);
            };

            shippingPointsService.searchArrivalShippingPointsByAddress = function (address) {
                return shippingPointsService.searchShippingPointsByAddress(address, 2);
            };

            shippingPointsService.searchArrivalShippingPointsByCoordinates = function (lat, lng) {
                return shippingPointsService.searchShippingPointsByCoordinates(lat, lng, 2);
            };

            shippingPointsService.searchArrivalShippingPointsByCoordinatesAndProduct = function (lat, lng, productId) {
                return Products.getShippingPoints({
                    id: productId,
                    lat: lat,
                    lng: lng,
                    search_type: 2,
                    _cache: new Date().getTime()
                }).$promise;
            };

            shippingPointsService.searchArrivalShippingPointsByAddressAndProduct = function (address, productId) {
                return Products.getShippingPoints({
                    id: productId,
                    address: address,
                    search_type: 2,
                    _cache: new Date().getTime()
                }).$promise;
            };

            shippingPointsService.searchShippingPointsByCoordinates = function (lat, lng, searchType) {
                return ShippingPoints.get({
                    lat: lat,
                    lng: lng,
                    search_type: searchType,
                    _cache: new Date().getTime()
                }).$promise;
            };

            shippingPointsService.searchShippingPointsByAddress = function (address, searchType) {
                return ShippingPoints.get({
                    address: address,
                    search_type: searchType,
                    _cache: new Date().getTime()
                }).$promise;
            };

            return shippingPointsService;
        }
    ]);
});
