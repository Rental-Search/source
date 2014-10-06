"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the items photos and info page.
     */
    angular.module("EloueDashboardApp").controller("ItemsInfoCtrl", [
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
        function ($scope, $stateParams, Endpoints, PrivateLife, SeatNumber, DoorNumber, Fuel, Transmission, Mileage, Consumption, Capacity, AddressesService, CategoriesService, PicturesService, ProductsService, PhoneNumbersService) {

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
                $scope.product = product;
                $scope.product.category = $scope.categoriesBaseUrl + $scope.product.categoryDetails.id + "/";
                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
                $scope.markListItemAsSelected();
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

            $scope.markListItemAsSelected = function() {
                $('li[id^="item-"]').each(function () {
                    var item = $(this);
                    if (item.attr("id") == ("item-" + $scope.product.id)) {
                        item.addClass("current");
                    } else {
                        item.removeClass("current");
                    }
                });
            };

            $scope.onPictureAdded = function () {
                PicturesService.savePicture($scope.product.id, $("#add-picture"), function (data) {
                    $scope.$apply(function () {
                        $scope.product.pictures.push(data);
                    });
                });
            };

            $scope.updateProduct = function () {
                ProductsService.updateProduct($scope.product);
                AddressesService.update($scope.product.addressDetails);
                PhoneNumbersService.updatePhoneNumber($scope.product.phoneDetails);
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
