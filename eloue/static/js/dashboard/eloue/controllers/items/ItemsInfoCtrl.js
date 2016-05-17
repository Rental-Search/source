define([
    "eloue/app",
    "../../../../common/eloue/values",
    "../../../../common/eloue/services/AddressesService",
    "../../../../common/eloue/services/CategoriesService",
    "../../../../common/eloue/services/PicturesService",
    "../../../../common/eloue/services/ProductsService",
    "../../../../common/eloue/services/UtilsService",
    "../../../../common/eloue/directives/Properties"
    
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the items photos and info page.
     */
    EloueDashboardApp.controller("ItemsInfoCtrl", [
        "$q",
        "$scope",
        "$stateParams",
        "Endpoints",
        "PrivateLife",
        "Fuel",
        "Transmission",
        "Mileage",
        "AddressesService",
        "CategoriesService",
        "PicturesService",
        "ProductsService",
        "UtilsService",
        "$log",
        function ($q, $scope, $stateParams, Endpoints, PrivateLife, Fuel, Transmission, Mileage, AddressesService, CategoriesService, PicturesService, ProductsService, UtilsService, $log) {

            $scope.rootCategories = {};
            $scope.nodeCategories = {};
            $scope.leafCategories = {};
            $scope.properties = [];
            $scope.rootCategory = {};
            $scope.nodeCategory = {};
            $scope.loadingPicture = 0;
            $scope.productsBaseUrl = Endpoints.api_url + "products/";
            $scope.categoriesBaseUrl = Endpoints.api_url + "categories/";
            $scope.isAuto = false;
            $scope.isRealEstate = false;
            $scope.privateLifeOptions = PrivateLife;
            $scope.seatNumberOptions = [
                {id: 2, name: "2"},
                {id: 3, name: "3"},
                {id: 4, name: "4"},
                {id: 5, name: "5"},
                {id: 6, name: "6"},
                {id: 7, name: "7"},
                {id: 8, name: "8"},
                {id: 9, name: "9"},
                {id: 10, name: "10"}
            ];
            $scope.doorNumberOptions = [
                {id: 2, name: "2"},
                {id: 3, name: "3"},
                {id: 4, name: "4"},
                {id: 5, name: "5"},
                {id: 6, name: "6"}
            ];
            $scope.fuelOptions = Fuel;
            $scope.transmissionOptions = Transmission;
            $scope.mileageOptions = Mileage;
            $scope.consumptionOptions = [
                {id: 2, name: "2"},
                {id: 3, name: "3"},
                {id: 4, name: "4"},
                {id: 5, name: "5"},
                {id: 6, name: "6"},
                {id: 7, name: "7"},
                {id: 8, name: "8"},
                {id: 9, name: "9"},
                {id: 10, name: "10"},
                {id: 11, name: "11"},
                {id: 12, name: "12"},
                {id: 13, name: "13"},
                {id: 14, name: "14"},
                {id: 15, name: "15"},
                {id: 16, name: "16"},
                {id: 17, name: "17"},
                {id: 18, name: "18"},
                {id: 19, name: "19"}
            ];
            $scope.capacityOptions = [
                {id: 1, name: "1"},
                {id: 2, name: "2"},
                {id: 3, name: "3"},
                {id: 4, name: "4"},
                {id: 5, name: "5"},
                {id: 6, name: "6"},
                {id: 7, name: "7"},
                {id: 8, name: "8"},
                {id: 9, name: "9"},
                {id: 10, name: "10"},
                {id: 11, name: "11"},
                {id: 12, name: "12"},
                {id: 13, name: "13"},
                {id: 14, name: "14"},
                {id: 15, name: "15"},
                {id: 16, name: "16"},
                {id: 17, name: "17"},
                {id: 18, name: "18"},
                {id: 19, name: "19+"}
            ];

            $scope.handleResponseErrors = function (error, object, action) {
                $scope.submitInProgress = false;
                $scope.showNotification(object, action, false);
            };

            ProductsService.getProductDetails($stateParams.id).then(
                function (product) {
                    $scope.applyProductDetails(product);
                }
            );

            $scope.applyProductDetails = function (product) {
                $scope.markListItemAsSelected("item-", $stateParams.id);
                $scope.markListItemAsSelected("item-tab-", "info");
                // Backend may send this fiels as string. It's wrong. The value
                // must be a number value.
                if (product && product.costs_per_km) {
                    product.costs_per_km = parseFloat(product.costs_per_km);
                }
                $scope.product = product;
                var initialCategoryId = product.category.id;
                CategoriesService.getParentCategory(product.category).then(function (nodeCategory) {
                    if (!nodeCategory.parent) {
                        $scope.nodeCategory = initialCategoryId;
                        $scope.rootCategory = nodeCategory.id;
                        $scope.updateNodeCategories(false);
                        $scope.updateFieldSet(nodeCategory);
                    } else {
                        $scope.nodeCategory = nodeCategory.id;
                        $scope.updateLeafCategories(false);
                        CategoriesService.getParentCategory(nodeCategory).then(function (rootCategory) {
                            $scope.rootCategory = rootCategory.id;
                            $scope.updateNodeCategories(false);
                            $scope.updateFieldSet(rootCategory);
                        });
                    }
                });
                $scope.properties = $scope.product.category.properties;
                $scope.product.category = $scope.categoriesBaseUrl + $scope.product.category.id + "/";
                $scope.product.addressDetails = $scope.product.address;
                $scope.product.phoneDetails = $scope.product.phone;
                if ($scope.product.first_registration_date) {
                    $scope.product.first_registration_date = Date.parse($scope.product.first_registration_date).toString("yyyy/MM/dd");
                }
                // Initiate custom scrollbars
                $scope.initCustomScrollbars();
            };

            CategoriesService.getRootCategories().then(function (categories) {
                $scope.rootCategories = categories;
            });

            $scope.onPictureAdded = function () {
                $scope.$apply(function () {
                    $scope.loadingPicture += 1;
                });
                PicturesService.savePicture($("#add-picture"), function (data) {
                    $scope.$apply(function () {
                        $scope.loadingPicture -= 1;
                        $scope.product.pictures.push(data);

                    });
                    $scope.showNotification("picture", "upload", true);
                    analytics.track('Item Photo Added', {
                        'product id': $scope.product.id,
                        'summary': $scope.product.summary,
                        'city': $scope.product.addressDetails.city,
                        'picture id': data.id,
                        'picture url': data.image.display
                    });
                }, function () {
                    $scope.$apply(function () {
                        $scope.loadingPicture -= 1;
                    });
                    $scope.showNotification("picture", "upload", false);
                });
            };

            $scope.updateProduct = function () {
                $scope.submitInProgress = true;
                $scope.product.address = Endpoints.api_url + "addresses/" + $scope.product.addressDetails.id + "/";
                if ($scope.product.phone && $scope.product.phone.id) {
                    $scope.product.phone = Endpoints.api_url + "phones/" + $scope.product.phone.id + "/";
                } else {
                    $scope.product.phone = null;
                }
                if ($scope.isAuto || $scope.isRealEstate) {
                    $scope.product.category = $scope.categoriesBaseUrl + $scope.nodeCategory + "/";
                    if ($scope.product.first_registration_date) {
                        $scope.product.first_registration_date = Date.parse($scope.product.first_registration_date).toString("yyyy-MM-dd");
                    }
                }
                var promises = [];
                promises.push(AddressesService.update($scope.product.addressDetails));
                promises.push(ProductsService.updateProduct($scope.product));
                $q.all(promises).then(function () {
                    $("#item-title-link-" + $scope.product.id).text($scope.product.summary);
                    $scope.submitInProgress = false;
                    $scope.showNotification("item_info", "save", true);

                    // Get the price by day                        
                    var price_by_day;
                    
                    angular.forEach($scope.product.prices, function (value, key) {
                        if (value.unit == 1) {
                            price_by_day = value.amount;
                        }
                    });

                    analytics.track('Item Info Updated', {
                        'product id': $scope.product.id,
                        'summary': $scope.product.summary,
                        'city': $scope.product.addressDetails.city,
                        'price by day': price_by_day
                    });

                }, function (error) {
                    // Special error which not allow to change some categories.
                    if (error.code == "10199") {
                        $scope.submitInProgress = false;
                        $scope.showNotificationMessage(error.description[0], false);
                    }
                    else {
                        $scope.handleResponseErrors(error, "item_info", "save");
                    }
                });
            };

            $scope.updateNodeCategories = function (reset) {
                if (reset) {
                    $scope.nodeCategory = undefined;
                }
                CategoriesService.getChildCategories($scope.rootCategory).then(function (categories) {
                    $scope.nodeCategories = categories;
                });
                CategoriesService.getCategory($scope.rootCategory).then(function (rootCategory) {
                    $scope.updateFieldSet(rootCategory);
                    if (reset){
                        $scope.properties = rootCategory.properties;    
                    }
                });
            };

            $scope.updateLeafCategories = function (reset) {
                if (reset) {
                    $scope.product.category = undefined;
                    CategoriesService.getCategory($scope.nodeCategory).then(function (nodeCategory) {
                        $scope.properties = nodeCategory.properties;
                    });
                }
                CategoriesService.getChildCategories($scope.nodeCategory).then(function (categories) {
                    $scope.leafCategories = categories;
                });
            };
            
            $scope.updateProperties = function(){ //$log.debug('updateProperties');
                //$log.debug($scope.product.category);
                CategoriesService.getCategory(UtilsService.getIdFromUrl($scope.product.category)).then(function (leafCategory) {
                    //$log.debug('leaf category:');
                    //$log.debug(leafCategory);
                    $scope.properties = leafCategory.properties;
                });
            };

            $scope.updateFieldSet = function (rootCategory) {
                $scope.isAuto = false;
                $scope.isRealEstate = false;
                if (rootCategory.name === "Automobile") {
                    $scope.isAuto = true;
                } else if (rootCategory.name === "Location saisonnière") {
                    $scope.isRealEstate = true;
                }
            };

            $scope.getTimes = function (n) {
                return new Array(n);
            };

            $scope.showRemoveConfirm = function (pictureId) {
                $scope.selectedPictureId = pictureId;
                $("#confirm").modal();
            };

            $scope.deletePicture = function () {
                $scope.submitInProgress = true;
                PicturesService.deletePicture($scope.selectedPictureId).then(function () {
                    ProductsService.getProductDetails($stateParams.id).then(function (product) {
                        $scope.submitInProgress = false;
                        $scope.product.pictures = product.pictures;
                    });
                    analytics.track('Item Photo Deleted', {
                        'product id': $scope.product.id,
                        'summary': $scope.product.summary,
                        'city': $scope.product.addressDetails.city
                    });
                }, function (error) {
                    $scope.handleResponseErrors(error, "picture", "delete");
                });
            };
        }
    ]);
});
