define(["angular-mocks", "eloue/controllers/items/ItemsShippingCtrl"], function () {

    describe("Controller: ItemsShippingCtrl", function () {

        var ItemsShippingCtrl,
            scope,
            stateParams,
            timeout,
            endpointsMock,
            productsLoadServiceMock,
            productShippingPointsServiceMock,
            sippingPointsServiceMock,
            usersServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {

            endpointsMock = {
                oauth_url: "http://10.0.5.47:8200/oauth2/",
                api_url: "http://10.0.5.47:8200/api/2.0/"
            };

            productsLoadServiceMock = {
                getProduct: function (productId, loadProductStats, loadOwnerStats) {
                    return {then: function () {
                        return {response: {}}
                    }}
                }
            };

            productShippingPointsServiceMock = {
                getByProduct: function (productId) {
                    return {then: function () {
                        return {response: {}}
                    }}
                },
                deleteShippingPoint: function (shippingPointId) {
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                },
                saveShippingPoint: function (shippingPoint) {
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };

            sippingPointsServiceMock = {
                searchDepartureShippingPointsByCoordinates: function(lat, lng) {
                    return {then: function () {
                        return {response: {}}
                    }}
                }
            };

            usersServiceMock = {
                getMe: function () {
                    console.log("usersServiceMock:getMe called");
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };

            module(function ($provide) {
                $provide.value("ProductsLoadService", productsLoadServiceMock);
                $provide.value("ProductShippingPointsService", productShippingPointsServiceMock);
                $provide.value("SippingPointsService", sippingPointsServiceMock);
                $provide.value("UsersService", usersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller, $timeout) {
            scope = $rootScope.$new();
            timeout = $timeout;
            scope.markListItemAsSelected = function (prefix, id) {
            };
            scope.initCustomScrollbars = function () {
            };
            stateParams = {
                id: 1
            };

            spyOn(productsLoadServiceMock, "getProduct").and.callThrough();
            spyOn(productShippingPointsServiceMock, "getByProduct").and.callThrough();
            spyOn(productShippingPointsServiceMock, "deleteShippingPoint").and.callThrough();
            spyOn(productShippingPointsServiceMock, "saveShippingPoint").and.callThrough();
            spyOn(sippingPointsServiceMock, "searchDepartureShippingPointsByCoordinates").and.callThrough();
            spyOn(usersServiceMock, "getMe").and.callThrough();

            ItemsShippingCtrl = $controller('ItemsShippingCtrl', { $scope: scope, $stateParams: stateParams, $timeout: timeout,
                Endpoints: endpointsMock, ProductsLoadService: productsLoadServiceMock, ProductShippingPointsService: productShippingPointsServiceMock,
                ShippingPointsService: sippingPointsServiceMock, UsersService: usersServiceMock});
        }));

        it("ItemsShippingCtrl should be not null", function () {
            expect(!!ItemsShippingCtrl).toBe(true);
        });
    });
});
