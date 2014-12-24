define(["angular-mocks", "datejs", "eloue/controllers/publish_item/PublishAdCtrl"], function () {

    describe("Controller: PublishAdCtrl", function () {

        var PublishAdCtrl,
            scope,
            window,
            location,
            endpointsMock,
            utilsServiceMock,
            unitMock,
            currencyMock,
            productsServiceMock,
            usersServiceMock,
            addressesServiceMock,
            authServiceMock,
            categoriesServiceMock,
            pricesServiceMock,
            toDashboardRedirectServiceMock,
            serverValidationServiceMock,
            scriptTagServiceMock;

        beforeEach(module("EloueWidgetsApp"));

        beforeEach(function () {
            endpointsMock = {
                api_url: "http://10.0.0.111:8000/api/2.0/"
            };
            unitMock = {DAY: {id: 1}};
            currencyMock = {};
            productsServiceMock = {};
            usersServiceMock = {};
            addressesServiceMock = {
                saveAddress:  function(address) {
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };
            authServiceMock = {
                getCookie: function (cookieName) {

                }
            };
            categoriesServiceMock = {
                getChildCategories: function(rootCategory) {
                    return {then: function () {
                        return {result: {}}
                    }}
                },
                getCategory: function(rootCategory) {
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };
            pricesServiceMock = {};
            toDashboardRedirectServiceMock = {};
            serverValidationServiceMock = {
                removeErrors: function() {},
                addError: function(field, description) {}
            };
            scriptTagServiceMock = {
                trackEvent: function (category, action, value) {},
                trackPageView: function () {},
                loadAdWordsTags: function (googleConversionLabel) {},
                loadPdltrackingScript: function (currentUserId) {}
            };

            module(function ($provide) {
                $provide.value("Endpoints", endpointsMock);
                $provide.value("Unit", unitMock);
                $provide.value("Currency", currencyMock);
                $provide.value("ProductsService", productsServiceMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("AuthService", authServiceMock);
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("PricesService", pricesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("ToDashboardRedirectService", toDashboardRedirectServiceMock);
                $provide.value("ServerValidationService", serverValidationServiceMock);
                $provide.value("ScriptTagService", scriptTagServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.currentUserPromise = {then: function () {
                return {response: {}}
            }};
            scope.currentUser = {
                id: 111,
                default_address: {
                    country: "FR"
                }
            };
            window = {location: {href: "location/sdsdfdfsdfsd/sdfsdfsd/sddfsdf/fdff-123"}};
            location = {};
            utilsServiceMock = {};
            spyOn(categoriesServiceMock, "getChildCategories").and.callThrough();
            spyOn(categoriesServiceMock, "getCategory").and.callThrough();
            spyOn(serverValidationServiceMock, "removeErrors").and.callThrough();
            spyOn(addressesServiceMock, "saveAddress").and.callThrough();
            spyOn(serverValidationServiceMock, "addError").and.callThrough();
            spyOn(scriptTagServiceMock, "trackEvent").and.callThrough();
            spyOn(scriptTagServiceMock, "trackPageView").and.callThrough();
            spyOn(scriptTagServiceMock, "loadAdWordsTags").and.callThrough();
            spyOn(scriptTagServiceMock, "loadPdltrackingScript").and.callThrough();
            PublishAdCtrl = $controller("PublishAdCtrl", {
                $scope: scope, $window: window, $location: location, Endpoints: endpointsMock,
                Unit: unitMock,
                Currency: currencyMock,
                ProductsService: productsServiceMock,
                UsersService: usersServiceMock,
                AddressesService: addressesServiceMock,
                AuthService: authServiceMock,
                CategoriesService: categoriesServiceMock,
                PricesService: pricesServiceMock,
                UtilsService: utilsServiceMock,
                ToDashboardRedirectService: toDashboardRedirectServiceMock,
                ServerValidationService: serverValidationServiceMock
            });
        }));

        it("PublishAdCtrl should be not null", function () {
            expect(!!PublishAdCtrl).toBe(true);
        });

        it("PublishAdCtrl:handleResponseErrors", function () {
            scope.handleResponseErrors();
        });

        it("PublishAdCtrl:setCategoryByLvl", function () {
            scope.setCategoryByLvl();
        });

        it("PublishAdCtrl:updateNodeCategories", function () {
            scope.updateNodeCategories();
        });

        it("PublishAdCtrl:updateLeafCategories", function () {
            scope.updateLeafCategories();
        });

        it("PublishAdCtrl:isCategorySelectorsValid", function () {
            scope.isCategorySelectorsValid();
        });

        it("PublishAdCtrl:publishAd(no default address)", function () {
            scope.noAddress = true;
            scope.publishAd();
        });

        it("PublishAdCtrl:publishAd", function () {
            scope.publishAd();
        });

        it("PublishAdCtrl:saveProduct", function () {
            scope.saveProduct();
        });

        it("PublishAdCtrl:updateFieldSet(auto)", function () {
            scope.updateFieldSet({name: "Automobile"});
            expect(scope.isAuto).toBeTruthy();
            expect(scope.isRealEstate).toBeFalsy();
        });

        it("PublishAdCtrl:updateFieldSet(real estate)", function () {
            scope.updateFieldSet({name: "Location saisonnière"});
            expect(scope.isAuto).toBeFalsy();
            expect(scope.isRealEstate).toBeTruthy();
        });

        it("PublishAdCtrl:searchCategory", function () {
            scope.searchCategory();
        });
    });
});
