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
        "UtilsService",
        "ToDashboardRedirectService",
        function ($scope, $window, $location, Endpoints, Unit, Currency, ProductsService, UsersService, AddressesService, AuthService, CategoriesService, PricesService, UtilsService, ToDashboardRedirectService) {

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

            /**
             * Show response errors on publish ad form under appropriate field.
             * @param error JSON object with error details
             */
            $scope.handleResponseErrors = function (error) {
                $scope.submitInProgress = false;
            };

            // Read authorization token
            $scope.currentUserToken = AuthService.getCookie("user_token");

            if (!!$scope.currentUserToken) {
                // Get current user
                $scope.currentUserPromise = UsersService.getMe().$promise;
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    if (!currentUser.default_address) {
                        $scope.noAddress = true;
                    }
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
                // load categories for comboboxes
                CategoriesService.getRootCategories().then(function (categories) {
                    if ($scope.currentUser && !$scope.currentUser.default_address) {
                        $scope.noAddress = true;
                    }
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

            /**
             * Update options for node category combobox
             */
            $scope.updateNodeCategories = function () {
                CategoriesService.getChildCategories($scope.rootCategory).then(function (categories) {
                    $scope.nodeCategories = categories;
                });
                CategoriesService.getCategory($scope.rootCategory).$promise.then(function (rootCategory) {
                    $scope.updateFieldSet(rootCategory);
                });
            };

            /**
             * Update options for leaf category combobox
             */
            $scope.updateLeafCategories = function () {
                CategoriesService.getChildCategories($scope.nodeCategory).then(function (categories) {
                    $scope.leafCategories = categories;
                });
            };

            /**
             * Publish product ad.
             */
            $scope.publishAd = function () {
                //if user has no default addrees, firstly save his address
                if ($scope.noAddress) {
                    $scope.submitInProgress = true;
                    $scope.currentUser.default_address.country = "FR";
                    AddressesService.saveAddress($scope.currentUser.default_address).$promise.then(function (result) {
                        $scope.currentUser.default_address = result;
                        UsersService.updateUser({default_address: Endpoints.api_url + "addresses/" + result.id + "/"});
                        $scope.saveProduct();
                    }, function (error) {
                        $scope.handleResponseErrors(error);
                    });
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
                        $scope.price.currency = Currency.EUR.name;
                        $scope.price.product = $scope.productsBaseUrl + product.id + "/";
                        PricesService.savePrice($scope.price).$promise.then(function (result) {
                            CategoriesService.getCategory(UtilsService.getIdFromUrl($scope.product.category)).$promise.then(function (productCategory) {
                                if ($scope.isAuto) {
                                    $scope.trackEvent("Dépôt annonce", "Voiture", productCategory.name);
                                    $scope.finishProductSaveAndRedirect(product);
                                } else if ($scope.isRealEstate) {
                                    $scope.trackEvent("Dépôt annonce", "Logement", productCategory.name);
                                    $scope.finishProductSaveAndRedirect(product);
                                } else {
                                    CategoriesService.getAncestors(UtilsService.getIdFromUrl($scope.product.category)).then(function(ancestors) {
                                        var categoriesStr = "";
                                        angular.forEach(ancestors, function (value, key) {
                                            categoriesStr = categoriesStr + value.name + " - ";
                                        });
                                        categoriesStr = categoriesStr + productCategory.name;
                                        $scope.trackEvent("Dépôt annonce", "Objet",  categoriesStr);
                                        $scope.finishProductSaveAndRedirect(product);
                                    });
                                }
                            });
                        }, function (error) {
                            $scope.handleResponseErrors(error);
                        });

                    }, function (error) {
                        $scope.handleResponseErrors(error);
                    });
                } else {
                    $scope.publishAdError = "All prices should be positive numbers!";
                    $scope.submitInProgress = false;
                }
            };

            /**
             * Add analytics tags on the page and redirect to dashboard item info page.
             * @param product product
             */
            $scope.finishProductSaveAndRedirect = function (product) {
                $scope.trackPageView();
                $scope.loadPdltrackingScript();
                $scope.loadAdWordsTagPublishAd();
                //TODO: redirects to the dashboard item detail page.
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
                //TODO: enable for auto and real estate
                if (!$scope.isAuto && !$scope.isRealEstate && $scope.rootCategory && $scope.product.summary && ($scope.product.summary.length > 1)) {
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

            /**
             * Add this tags when a user succeeded to post a new product:
             * <script type="text/javascript" src="https://lead.pdltracking.com/?lead_id={{product.owner.pk}}%&tt=javascript&sc=1860"></script>
             <script type="text/javascript" src="https://lead.pdltracking.com/?lead_id={{product.owner.pk}}&tt=javascript&sc=1859"></script>
             <noscript>
             <img src="https://lead.pdltracking.com/?lead_id={{product.owner.pk}}&tt=pixel&sc=1859" width="1" height="1" border="0" />
             </noscript>
             <IMG SRC="https://clic.reussissonsensemble.fr/registersale.asp?site=13625&mode=ppl&ltype=1&order=TRACKING_NUMBER" WIDTH="1" HEIGHT="1" />
             <script type="text/javascript" id="affilinet_advc">
             var type = "Checkout";
             var site = "13625";
             </script>
             <script type="text/javascript" src="https://clic.reussissonsensemble.fr/art/JS/param.aspx"></script>
             <script src="//l.adxcore.com/a/track_conversion.php?annonceurid=21679"></script>
             <noscript>
             <img src="//l.adxcore.com/a/track_conversion.php?adsy=1&annonceurid=21679">
             </noscript>
             */
            $scope.loadPdltrackingScript = function () {
                var script1860 = document.createElement("script");
                script1860.type = "text/javascript";
                script1860.src = "https://lead.pdltracking.com/?lead_id=" + $scope.currentUser.id + "&tt=javascript&sc=1860";
                document.body.appendChild(script1860);

                var script1859 = document.createElement("script");
                script1859.type = "text/javascript";
                script1859.src = "https://lead.pdltracking.com/?lead_id=" + $scope.currentUser.id + "%&tt=javascript&sc=1859";
                document.body.appendChild(script1859);

                var noscript1859 = document.createElement("noscript");
                var img1859 = document.createElement("img");
                img1859.src = "https://lead.pdltracking.com/?lead_id=" + $scope.currentUser.id + "&tt=pixel&sc=1859";
                img1859.width = "1";
                img1859.height = "1";
                img1859.border = "0";
                noscript1859.appendChild(img1859);
                document.body.appendChild(noscript1859);

                var img13625 = document.createElement("img");
                img13625.src = "https://clic.reussissonsensemble.fr/registersale.asp?site=13625&mode=ppl&ltype=1&order=TRACKING_NUMBER";
                img13625.width = "1";
                img13625.height = "1";
                document.body.appendChild(img13625);

                var scriptAffilinet = document.createElement("script");
                scriptAffilinet.type = "text/javascript";
                scriptAffilinet.id = "affilinet_advc";
                var code = "var type = 'Checkout';" +
                    "var site = '13625';";
                try {
                    scriptAffilinet.appendChild(document.createTextNode(code));
                    document.body.appendChild(scriptAffilinet);
                } catch (e) {
                    scriptAffilinet.text = code;
                    document.body.appendChild(scriptAffilinet);
                }

                var scriptClic = document.createElement("script");
                scriptClic.type = "text/javascript";
                scriptClic.src = "https://clic.reussissonsensemble.fr/art/JS/param.aspx";
                document.body.appendChild(scriptClic);

                var scriptAnnonceur = document.createElement("script");
                scriptAnnonceur.src = "//l.adxcore.com/a/track_conversion.php?annonceurid=21679";
                document.body.appendChild(scriptAnnonceur);

                var noscriptAnnonceur = document.createElement("noscript");
                var imgAnnonceur = document.createElement("img");
                imgAnnonceur.src = "//l.adxcore.com/a/track_conversion.php?adsy=1&annonceurid=21679";
                noscriptAnnonceur.appendChild(imgAnnonceur);
                document.body.appendChild(noscriptAnnonceur);
            };

            /**
             * Add Google ad scripts.
             */
            $scope.loadAdWordsTagPublishAd = function () {
                var scriptAdWords = document.createElement("script");
                scriptAdWords.type = "text/javascript";
                var code = "/* <![CDATA[ */" +
                    "var google_conversion_id = 1027691277;" +
                    "var google_conversion_language = 'en';" +
                    "var google_conversion_format = '3';" +
                    "var google_conversion_color = 'ffffff';" +
                    "var google_conversion_label = 'SfnGCMvgrgMQjaaF6gM';" +
                    "var google_conversion_value = 1.00;" +
                    "var google_conversion_currency = 'EUR';" +
                    "var google_remarketing_only = false;" +
                    "/* ]]> */";
                try {
                    scriptAdWords.appendChild(document.createTextNode(code));
                    document.body.appendChild(scriptAdWords);
                } catch (e) {
                    scriptAdWords.text = code;
                    document.body.appendChild(scriptAdWords);
                }

                var scriptConversion = document.createElement("script");
                scriptConversion.type = "text/javascript";
                scriptConversion.src = "//www.googleadservices.com/pagead/conversion.js";
                document.body.appendChild(scriptConversion);

                var noscriptConversion = document.createElement("noscript");
                var divConversion = document.createElement("div");
                divConversion.style = "display:inline;";
                var imgConversion = document.createElement("img");
                imgConversion.src = "//www.googleadservices.com/pagead/conversion/1027691277/?value=1.00&amp;currency_code=EUR&amp;label=SfnGCMvgrgMQjaaF6gM&amp;guid=ON&amp;script=0";
                imgConversion.width = "1";
                imgConversion.height = "1";
                imgConversion.style = "border-style:none;";
                imgConversion.alt = "";
                divConversion.appendChild(imgConversion);
                noscriptConversion.appendChild(divConversion);
                document.body.appendChild(noscriptConversion);
            };

            /**
             * Push track event to Google Analytics.
             *
             * @param category category
             * @param action action
             * @param value value
             */
            $scope.trackEvent = function (category, action, value) {
                _gaq.push(["_trackEvent", category, action, value]);
            };

            /**
             * Push track page view to Google Analytics.
             */
            $scope.trackPageView = function () {
                _gaq.push(["_trackPageview", $window.location.href + "/success/"]);
            };
        }])
});
