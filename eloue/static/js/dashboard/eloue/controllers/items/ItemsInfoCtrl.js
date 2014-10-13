"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items photos and info page.
     */
    angular.module("EloueDashboardApp").controller("ItemsInfoCtrl", [
        "$q",
        "$scope",
        "$stateParams",
        "Endpoints",
        "PrivateLife",
        "SeatNumber",
        "DoorNumber",
        "Fuel",
        "Transmission",
        "Mileage",
        "Consumption",
        "Capacity",
        "AddressesService",
        "CategoriesService",
        "PicturesService",
        "ProductsService",
        "PhoneNumbersService",
        function ($q, $scope, $stateParams, Endpoints, PrivateLife, SeatNumber, DoorNumber, Fuel, Transmission, Mileage, Consumption, Capacity, AddressesService, CategoriesService, PicturesService, ProductsService, PhoneNumbersService) {

            $scope.rootCategories = {};
            $scope.nodeCategories = {};
            $scope.leafCategories = {};
            $scope.rootCategory = {};
            $scope.nodeCategory = {};
            $scope.productsBaseUrl = Endpoints.api_url + "products/";
            $scope.categoriesBaseUrl = Endpoints.api_url + "categories/";
            $scope.isAuto = false;
            $scope.isRealEstate = false;
            $scope.privateLifeOptions = PrivateLife;
            $scope.seatNumberOptions = SeatNumber;
            $scope.doorNumberOptions = DoorNumber;
            $scope.fuelOptions = Fuel;
            $scope.transmissionOptions = Transmission;
            $scope.mileageOptions = Mileage;
            $scope.consumptionOptions = Consumption;
            $scope.capacityOptions = Capacity;

            ProductsService.getProductDetails($stateParams.id).then(function (product) {
                $scope.markListItemAsSelected("item-", $stateParams.id);
                $scope.product = product;
                $scope.product.category = $scope.categoriesBaseUrl + $scope.product.categoryDetails.id + "/";
                $scope.product.addressDetails = $scope.product.address;
                $scope.product.phoneDetails = $scope.product.phone;
                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
                CategoriesService.getParentCategory($scope.product.categoryDetails).$promise.then(function (nodeCategory) {
                    $scope.nodeCategory = nodeCategory.id;
                    $scope.updateLeafCategories();
                    CategoriesService.getParentCategory(nodeCategory).$promise.then(function (rootCategory) {
                        $scope.rootCategory = rootCategory.id;
                        $scope.updateNodeCategories();
                        $scope.updateFieldSet(rootCategory);
                    });
                });

            });

            CategoriesService.getRootCategories().then(function (categories) {
                $scope.rootCategories = categories;
            });

            $scope.onPictureAdded = function () {
                PicturesService.savePicture($scope.product.id, $("#add-picture"), function (data) {
                    $scope.$apply(function () {
                        $scope.product.pictures.push(data);
                    });
                });
            };

            $scope.updateProduct = function () {
                $scope.submitInProgress = true;
                $scope.product.address = Endpoints.api_url + "addresses/" + $scope.product.address.id + "/";
                $scope.product.phone = Endpoints.api_url + "phones/" + $scope.product.phone.id + "/";
                var promises = [];
                promises.push(AddressesService.update($scope.product.addressDetails).$promise);
                promises.push(ProductsService.updateProduct($scope.product).$promise);
                $q.all(promises).then(function(results) {
                    $scope.submitInProgress = false;
                });
            };

            $scope.updateNodeCategories = function () {
                CategoriesService.getChildCategories($scope.rootCategory).then(function (categories) {
                    $scope.nodeCategories = categories;
                });
                CategoriesService.getCategory($scope.rootCategory).$promise.then(function (rootCategory) {
                    $scope.updateFieldSet(rootCategory);
                });
            };

            $scope.updateLeafCategories = function () {
                CategoriesService.getChildCategories($scope.nodeCategory).then(function (categories) {
                    $scope.leafCategories = categories;
                });
            };

            $scope.updateFieldSet = function (rootCategory) {
                $scope.isAuto = false;
                $scope.isRealEstate = false;
                if (rootCategory.name === "Automobile") {
                    $scope.isAuto = true;
                } else if (rootCategory.name === "Hébergement") {
                    $scope.isRealEstate = true;
                }
            }
        }
    ]);
});
