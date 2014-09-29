define(["angular", "eloue/modules/booking/BookingModule",
    "../../../../../common/eloue/values",
    "../../../../../common/eloue/services"
], function (angular) {
    "use strict";

    angular.module("EloueApp.BookingModule").controller("PublishAdCtrl", [
        "$scope",
        "$window",
        "$location",
        "Endpoints",
        "Unit",
        "Currency",
        "ProductsService",
        "UsersService",
        "AuthService",
        "CategoriesService",
        "PricesService",
        function ($scope, $window, $location, Endpoints, Unit, Currency, ProductsService, UsersService, AuthService, CategoriesService, PricesService) {

            $scope.rootCategories = {};
            $scope.nodeCategories = {};
            $scope.leafCategories = {};
            $scope.rootCategory = {};
            $scope.nodeCategory = {};
            $scope.productsBaseUrl = Endpoints.api_url + "products/";
            $scope.categoriesBaseUrl = Endpoints.api_url + "categories/";
            $scope.product = {};
            $scope.isAuto = false;
            $scope.isRealEstate = false;
            $scope.price = {
                id: null, amount: null, unit: Unit.DAY.id
            };

            // Read authorization token
            $scope.currentUserToken = AuthService.getCookie("user_token");

            if (!!$scope.currentUserToken) {
                // Get current user
                $scope.currentUserPromise = UsersService.getMe().$promise;
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                });
            }

            $scope.$on("openModal", function (event, args) {
                var params = args.params;
                var rootCategoryId = params.category;
                if (!!rootCategoryId) {
                    CategoriesService.getRootCategories().$promise.then(function (categories) {
                        $scope.rootCategories = categories.results;
                        $scope.rootCategory = rootCategoryId;
                        $scope.updateNodeCategories();
                    });
                }
            });

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

            $scope.publishAd = function() {
                console.log("Publish ad");
                ProductsService.saveProduct($scope.product).$promise.then(function(result) {
                    //TODO: finish and check saving product and price
                    $scope.price.currency = Currency.EUR.name;
                    $scope.price.product = $scope.productsBaseUrl + result.id + "/";
                    PricesService.savePrice($scope.price).$promise.then(function(result) {
                        //TODO: redirects to the dashboard item detail page.
                        $(".modal").modal("hide");
                    });
                });
            };

            $scope.updateFieldSet = function (rootCategory) {
                console.log(rootCategory);
                $scope.isAuto = false;
                $scope.isRealEstate = false;
                if (rootCategory.name === "Automobile") {
                    $scope.isAuto = true;
                } else if (rootCategory.name === "Hébergement") {
                    $scope.isRealEstate = true;
                }
            };

            $scope.searchCategory = function(event) {
                //TODO: search appropriate category by $scope.product.summary
            }
        }])
});
