define([
    "eloue/app",
    "../../../../../bower_components/toastr/toastr",
    "../../../../common/eloue/values",
    "../../../../common/eloue/services/ProductsService",
    "../../../../common/eloue/services/UsersService",
    "../../../../common/eloue/services/AddressesService",
    "../../../../common/eloue/services/PhoneNumbersService",
    "../../../../common/eloue/services/AuthService",
    "../../../../common/eloue/services/CategoriesService",
    "../../../../common/eloue/services/PricesService",
    "../../../../common/eloue/services/UtilsService",
    "../../../../common/eloue/services/ToDashboardRedirectService",
    "../../../../common/eloue/services/ServerValidationService",
    "../../../../common/eloue/services/ScriptTagService",
    "../../../../common/eloue/directives/Properties"
], function (EloueWidgetsApp, toastr) {
    "use strict";
    
    EloueWidgetsApp.controller("PublishAdCtrl", [
        "$scope",
        "$q",
        "$window",
        "$location",
        "Endpoints",
        "Unit",
        "Currency",
        "ProductsService",
        "UsersService",
        "AddressesService",
        "PhoneNumbersService",
        "AuthService",
        "CategoriesService",
        "PricesService",
        "UtilsService",
        "ToDashboardRedirectService",
        "ServerValidationService",
        "ScriptTagService",
        "MapsService",
        "$log",
        function ($scope, $q, $window, $location, Endpoints, Unit, Currency, ProductsService, UsersService, AddressesService, PhoneNumbersService, AuthService, CategoriesService, PricesService, UtilsService, ToDashboardRedirectService, ServerValidationService, ScriptTagService, MapsService, $log) {

            $scope.submitInProgress = false;
            $scope.publishAdError = null;
            $scope.rootCategories = [];
            $scope.nodeCategories = [];
            $scope.leafCategories = [];
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
            $scope.phonesBaseUrl = Endpoints.api_url + "phones/";
            $scope.addressesBaseUrl = Endpoints.api_url + "addresses/";
            $scope.product = {};
            $scope.isAuto = false;
            $scope.isRealEstate = false;
            $scope.price = {
                id: null,
                amount: null,
                unit: Unit.DAY.id
            };

            $scope.errors = {
                summary: "",
                brand: "",
                model: "",
                category: "",
                street: "",
                zipcode: "",
                amount: "",
                deposit_amount: "",
                km_included: "",
                costs_per_km: "",
                first_registration_date: "",
                licence_plate: "",
                tax_horsepower: ""
            };
            
            $scope.properties = [];
            
            /**
             * Activate geolocation search.
             */
            $window.googleMapsLoaded = function () {
                $("#geolocate").formmapper({
                    details: "form"
                });
            };

            /**
             * Show response errors on publish ad form under appropriate field.
             * @param error JSON object with error details
             */
            $scope.handleResponseErrors = function (error) {
                $scope.submitInProgress = false;
            };

            // Read authorization token
            $scope.currentUserToken = AuthService.getUserToken();

            if (!!$scope.currentUserToken) {
                // Get current user
                $scope.currentUserPromise = UsersService.getMe();
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    if (!currentUser.default_address) {
                        $scope.noAddress = true;
                    }
                    if (!currentUser.default_number) {
                        $scope.noPhone = true;
                    }
                });
            }

            $scope.setCategoryByLvl = function (categoryId, level) {
                switch (level) {
                    case 1:
                        $scope.nodeCategory = categoryId;
                        $scope.updateLeafCategories();
                        break;
                    case 2:
                        $scope.product.category = categoryId;
                        break;
                    default:
                        $scope.rootCategory = categoryId;
                        $scope.updateNodeCategories();
                }
            };

            /**
             * Load necessary data on modal window open event based on modal name.
             */
            $scope.$on("openModal", function (event, args) {
                $scope.openModal(args.name, args.params.category);
            });

            $scope.openModal = function (name, categoryId) {
                var currentUserToken = AuthService.getUserToken(), modalContainer;
                if (!currentUserToken && name !== "login") {
                    AuthService.saveAttemptUrl(name, {category: categoryId});
                    name = "login";
                } else {
                    //var rootCategoryId = params.category;
                    $scope.product = {};
                    $scope.price = {
                        id: null,
                        amount: null,
                        unit: Unit.DAY.id
                    };
                    $scope.publishAdError = null;
                    // load categories for comboboxes
                    CategoriesService.getRootCategories().then(function (categories) {
                        if ($scope.currentUser) {
                            if (!$scope.currentUser.default_address) {
                                $scope.noAddress = true;
                            }
                            if (!$scope.currentUser.default_number) {
                                $scope.noPhone = true;
                            }
                        }
                        $scope.rootCategories = categories;

                        if (!!categoryId && categoryId !== "") {
                            CategoriesService.getAncestors(categoryId).then(
                                function (categories) {
                                    $scope.processCategoryAncestors(categories, categoryId);
                                }
                            );
                        } else if ($scope.rootCategory) {
                            $scope.updateNodeCategories();
                        }
                    });
                }
                if (name) {
                    $(".modal").modal("hide");
                    modalContainer = $("#" + name + "Modal");
                    modalContainer.modal("show");

                    //Segment Publish Item Modal
                    analytics.track('Publish Item Modal');
                }
            };

            $scope.processCategoryAncestors = function (categories, categoryId) {
                var level = 0;
                angular.forEach(categories, function (value) {
                    $scope.setCategoryByLvl(value.id, level);
                    level += 1;
                });
                $scope.setCategoryByLvl(categoryId, level);
            };

            /**
             * Restore path when closing modal window.
             */
            $scope.$on("closeModal", function (event, args) {
                var currentPath = $location.path(), newPath = currentPath.slice(0, currentPath.indexOf(args.name));
                $location.path(newPath);
                $scope.$apply();
            });
            
            /**
             * Update options for node category combobox
             */
            $scope.updateNodeCategories = function () {
                $scope.nodeCategory = undefined;
                CategoriesService.getChildCategories($scope.rootCategory).then(function (categories) {
                    $scope.nodeCategories = categories;
                });
                CategoriesService.getCategory($scope.rootCategory).then(function (rootCategory) {
                    $scope.updateFieldSet(rootCategory);
                    //$log.debug('root category:');
                    // $log.debug(rootCategory);
                    $scope.properties = rootCategory.properties;
                });
            };

            /**
             * Update options for leaf category combobox
             */
            $scope.updateLeafCategories = function () {
                $scope.product.category = undefined;
                CategoriesService.getChildCategories($scope.nodeCategory).then(function (categories) {
                    $scope.leafCategories = categories;
                });
                CategoriesService.getCategory($scope.nodeCategory).then(function (nodeCategory) {
                    // $log.debug('node category:');
                    $scope.properties = nodeCategory.properties;
                });
            };
            
            
            /**
             * Update category properties from leaf category
             */
            $scope.updateProperties = function(){ $log.debug('updateProperties');
                // $log.debug($scope.product.category);
                CategoriesService.getCategory(UtilsService.getIdFromUrl($scope.product.category)).then(function (leafCategory) {
                    // $log.debug('leaf category:');
                    //$log.debug(leafCategory);
                    $scope.properties = leafCategory.properties;
                });
            };

            $scope.isCategorySelectorsValid = function () {
                return !!$scope.rootCategories && !!$scope.rootCategory &&
                    ((!!$scope.nodeCategories && $scope.nodeCategories.length > 0 && !!$scope.nodeCategory) ||
                    (!$scope.nodeCategories || $scope.nodeCategories.length === 0)) &&
                    ((!!$scope.leafCategories && $scope.leafCategories.length > 0 && !!$scope.product.category) ||
                    (!$scope.leafCategories || $scope.leafCategories.length === 0));
            };

            /**
             * Publish product ad.
             */
            $scope.publishAd = function () {
                
                var publishPromise = $q.defer().promise;
                
                // Add required user info
                if ($scope.noAddress || $scope.noPhone) {
                    
                    $scope.submitInProgress = true;
                    
                    var patchPromises = {};
                    
                    if ($scope.noAddress){
                        $scope.currentUser.default_address.country = "FR";
                        patchPromises.default_address = AddressesService
                                .saveAddress($scope.currentUser.default_address)
                                .then(function(result){
                                    $scope.currentUser.default_address = result;
                                    return UsersService.updateUser({
                                        default_address: $scope.addressesBaseUrl + result.id + "/"
                                    });
                            });
                    };

                    if ($scope.noPhone){
                        patchPromises.default_number = PhoneNumbersService
                                .savePhoneNumber($scope.currentUser.default_number)
                                .then(function(result){
                                    $scope.currentUser.default_number = result;
                                    return UsersService.updateUser({
                                        default_number: $scope.phonesBaseUrl + result.id + "/"
                                    });
                            });
                    };
                    
                    $q.all(patchPromises)
                        .catch($scope.handleResponseErrors)
                        .then($scope.saveProduct);
                    
                } else {
                    $scope.saveProduct();
                }
                
            };

            /**
             * Save product and price info.
             */
            $scope.saveProduct = function () {
                $scope.submitInProgress = true;
                $scope.product.description = "";
                $scope.product.address = $scope.addressesBaseUrl + $scope.currentUser.default_address.id + "/";
                if ($scope.price.amount > 0) {
                    if (!$scope.leafCategories || $scope.leafCategories.length === 0) {
                        if (!!$scope.nodeCategories && $scope.nodeCategories.length > 0) {
                            $scope.product.category = $scope.categoriesBaseUrl + $scope.nodeCategory + "/";
                        } else {
                            $scope.product.category = $scope.categoriesBaseUrl + $scope.rootCategory + "/";
                        }
                    }
                    if ($scope.isAuto || $scope.isRealEstate) {
                        $scope.product.category = $scope.categoriesBaseUrl + $scope.nodeCategory + "/";
                    }
                    if ($scope.isAuto) {
                        $scope.product.summary = $scope.product.brand + " " + $scope.product.model;
                        $scope.product.first_registration_date = Date.parse($scope.product.first_registration_date).toString("yyyy-MM-dd");
                    }


                    ProductsService.saveProduct($scope.product).then(
                        function (product) {
                            $scope.price.currency = $scope.product.currency;
                            $scope.price.product = $scope.productsBaseUrl + product.id + "/";
                            PricesService.savePrice($scope.price).then(
                                function () {
                                    CategoriesService.getCategory(UtilsService.getIdFromUrl($scope.product.category)).then(
                                        function (productCategory) {
                                            $scope.trackPublishAdEvent(product, productCategory);
                                        }
                                    );
                                },
                                $scope.handleResponseErrors
                            );

                        },
                        $scope.handleResponseErrors
                    );
                } else {
                    //$scope.publishAdError = "All prices should be positive numbers!";
                    ServerValidationService.removeErrors();
                    ServerValidationService.addError("amount", "Value can't be negative");

                    $scope.submitInProgress = false;
                }
            };

            $scope.trackPublishAdEvent = function (product, productCategory) {
                if ($scope.isAuto) {
                    ScriptTagService.trackEvent("Dépôt annonce", "Voiture", productCategory.name);
                    $scope.finishProductSaveAndRedirect(product);
                } else if ($scope.isRealEstate) {
                    ScriptTagService.trackEvent("Dépôt annonce", "Logement", productCategory.name);
                    $scope.finishProductSaveAndRedirect(product);
                } else {
                    CategoriesService.getAncestors(UtilsService.getIdFromUrl($scope.product.category)).then(
                        function (ancestors) {
                            $scope.trackPublishSimpleAdEvent(ancestors, productCategory, product);
                        }
                    );
                }
                // Segment track published item
                ProductsService.getProductDetails(product.id).then(
                    function (result) {
                        // Get the price by day                        
                        var price_by_day;
                        
                        angular.forEach(result.prices, function (value, key) {
                            if (value.unit == 1) {
                                price_by_day = value.amount;
                            }
                        });

                        analytics.track('Published Item', {
                            'product id': result.id,
                            'summary': result.summary,
                            'category name': result.category.name,
                            'category slug': result.category.slug,
                            'city': result.address.city,
                            'price by day': price_by_day
                        });
                    }
                );
            };

            $scope.trackPublishSimpleAdEvent = function (ancestors, productCategory, product) {
                var categoriesStr = "";
                angular.forEach(ancestors, function (value) {
                    categoriesStr = categoriesStr + value.name + " - ";
                });
                categoriesStr = categoriesStr + productCategory.name;
                ScriptTagService.trackEvent("Dépôt annonce", "Objet", categoriesStr);
                $scope.finishProductSaveAndRedirect(product);
            };

            /**
             * Add analytics tags on the page and redirect to dashboard item info page.
             * @param product product
             */
            $scope.finishProductSaveAndRedirect = function (product) {
                ScriptTagService.trackPageView();
                ScriptTagService.loadPdltrackingScript($scope.currentUser.id);
                ScriptTagService.loadAdWordsTags("EO41CNPrpQMQjaaF6gM");
                toastr.options.positionClass = "toast-top-full-width";
                toastr.success("Annonce publiée", "");
                $(".modal").modal("hide");
                //$window.location.href = "/dashboard/#/items/" + product.id + "/info";

                $scope.submitInProgress = false;
                ToDashboardRedirectService.showPopupAndRedirect("/dashboard/#/items/" + product.id + "/info");
            };

            /**
             * Update publish ad form according to selected root category.
             * @param rootCategory product root category
             */
            $scope.updateFieldSet = function (rootCategory) {
                $scope.isAuto = false;
                $scope.isRealEstate = false;
                if (rootCategory.name === "Automobile") {
                    $scope.isAuto = true;
                } else if (rootCategory.name === "Location saisonnière") {
                    $scope.isRealEstate = true;
                }
            };

            /**
             * Search for node and leaf categories suggestions based on entered product title.
             */
            $scope.searchCategory = function () {
                if (!$scope.isAuto && !$scope.isRealEstate && $scope.rootCategory && $scope.product.summary && ($scope.product.summary.length > 1)) {
                    CategoriesService.searchByProductTitle($scope.product.summary, $scope.rootCategory).then(
                        $scope.applySuggestedCategories
                    );
                }
            };

            $scope.applySuggestedCategories = function (categories) {
                if (categories && categories.length > 0) {
                    var nodeCategoryList = [], leafCategoryList = [];
                    angular.forEach(categories, function (value) {
                        nodeCategoryList.push({id: value[1].id, name: value[1].name});
                        leafCategoryList.push({id: value[2].id, name: value[2].name});
                    });
                    $scope.nodeCategories = nodeCategoryList;
                    $scope.leafCategories = leafCategoryList;
                }
            };

            $scope.initRootCategory = function(rootCategoryId) {
                $scope.rootCategory = rootCategoryId;
                $scope.updateNodeCategories();
            };

            MapsService.loadGoogleMaps();
        }]);
});
