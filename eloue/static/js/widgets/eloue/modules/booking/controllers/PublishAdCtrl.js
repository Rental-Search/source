define(["angular", "toastr", "eloue/modules/booking/BookingModule",
    "../../../../../common/eloue/values",
    "../../../../../common/eloue/services"
], function (angular, toastr) {
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
        "AddressesService",
        "AuthService",
        "CategoriesService",
        "PricesService",
        function ($scope, $window, $location, Endpoints, Unit, Currency, ProductsService, UsersService, AddressesService, AuthService, CategoriesService, PricesService) {

            $scope.submitInProgress = false;
            $scope.publishAdError = null;
            $scope.rootCategories = {};
            $scope.nodeCategories = {};
            $scope.leafCategories = {};
            $scope.rootCategory = {};
            $scope.nodeCategory = {};
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

            /**
             * Load necessary data on modal window open event based on modal name.
             */
            $scope.$on("openModal", function (event, args) {
                var params = args.params;
                var rootCategoryId = params.category;
                $scope.product = {};
                $scope.price = {
                    id: null, amount: null, unit: Unit.DAY.id
                };
                $scope.publishAdError = null;
                CategoriesService.getRootCategories().then(function (categories) {
                    $scope.rootCategories = categories;
                    if (!!rootCategoryId) {
                        $scope.rootCategory = rootCategoryId;
                        $scope.updateNodeCategories();
                    }
                });
            });

            /**
             * Restore path when closing modal window.
             */
            $scope.$on("closeModal", function (event, args) {
                var currentPath = $location.path();
                var newPath = currentPath.slice(0, currentPath.indexOf(args.name));
                $location.path(newPath);
                $scope.$apply();
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

            $scope.publishAd = function () {
                console.log("Publish ad");
                if (!$scope.currentUser.default_address) {
                    $scope.currentUser.default_address.country = "FR";
                    AddressesService.saveAddress($scope.currentUser.default_address).$promise.then(function (result) {
                        $scope.currentUser.default_address = result;
                        UsersService.updateUser({default_address: Endpoints.api_url + "addresses/" + result.id + "/"});
                        $scope.saveProduct();
                    });
                } else {
                    $scope.saveProduct();
                }
            };

            $scope.saveProduct = function () {
                $scope.submitInProgress = true;
                $scope.product.description = "";
                $scope.product.address = Endpoints.api_url + "addresses/" + $scope.currentUser.default_address.id + "/";
                if ($scope.price.amount > 0) {
                    if ($scope.isAuto || $scope.isRealEstate) {
                        $scope.product.category = $scope.categoriesBaseUrl + $scope.nodeCategory + "/";
                    }
                    if ($scope.isAuto) {
                        $scope.product.summary = $scope.product.brand + " " + $scope.product.model;
                        $scope.product.first_registration_date = Date.parse($scope.product.first_registration_date).toString("yyyy-MM-dd");
                    }
                    ProductsService.saveProduct($scope.product).$promise.then(function (product) {
                        //TODO: finish and check saving product and price
                        $scope.price.currency = Currency.EUR.name;
                        $scope.price.product = $scope.productsBaseUrl + product.id + "/";

                        PricesService.savePrice($scope.price).$promise.then(function (result) {
                            //TODO: redirects to the dashboard item detail page.
                            toastr.options.positionClass = "toast-top-full-width";
                            toastr.success("Annonce publiée", "");
                            $(".modal").modal("hide");
                            $window.location.href = "/dashboard/#/items/" + product.id + "/info";
                            $scope.submitInProgress = false;
                        });

                    });
                } else {
                    $scope.publishAdError = "All prices should be positive numbers!";
                    $scope.submitInProgress = false;
                }
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

            $scope.searchCategory = function () {
                //TODO: enable for auto and real estate
                if (!$scope.isAuto && !$scope.isRealEstate &&$scope.rootCategory && $scope.product.summary && ($scope.product.summary.length > 1)) {
                    CategoriesService.searchByProductTitle($scope.product.summary, $scope.rootCategory).then(function (categories) {
                        if (categories && categories.length > 0) {
                            var nodeCategoryList = [];
                            var leafCategoryList = [];
                            angular.forEach(categories, function (value, key) {
                                nodeCategoryList.push({id: value[1].id, name: value[1].name});
                                leafCategoryList.push({id: value[2].id, name: value[2].name});

                            });
                            $scope.nodeCategories = nodeCategoryList;
                            $scope.leafCategories = leafCategoryList;
                        }
                    });
                }
            };

            $("#first_registration_date").datepicker({
                language: "fr",
                autoclose: true,
                todayHighlight: true
            });
        }])
});
