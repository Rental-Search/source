define(["angular-mocks", "eloue/controllers/items/ItemsShippingCtrl"], function () {

    describe("Controller: ItemsShippingCtrl", function () {

        var ItemsShippingCtrl,
            scope,
            stateParams,
            timeout,
            endpointsMock,
            productsServiceMock,
            productShippingPointsServiceMock,
            sippingPointsServiceMock,
            usersServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {

            endpointsMock = {
                oauth_url: "http://10.0.5.47:8200/oauth2/",
                api_url: "http://10.0.5.47:8200/api/2.0/"
            };

            productsServiceMock = {
                getProduct: function (productId, loadProductStats, loadOwnerStats) {
                    return simpleServiceResponse;
                }
            };

            productShippingPointsServiceMock = {
                getByProduct: function (productId) {
                    return simpleServiceResponse;
                },
                deleteShippingPoint: function (shippingPointId) {
                    return simpleServiceResponse;
                },
                saveShippingPoint: function (shippingPoint) {
                    return simpleServiceResponse;
                }
            };

            sippingPointsServiceMock = {
                searchDepartureShippingPointsByCoordinates: function(lat, lng) {
                    return simpleServiceResponse;
                }
            };

            usersServiceMock = {
                getMe: function () {
                    console.log("usersServiceMock:getMe called");
                    return simpleServiceResponse;
                }
            };

            module(function ($provide) {
                $provide.value("ProductsService", productsServiceMock);
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
            scope.showNotification = function(object, action, bool){};
            spyOn(productsServiceMock, "getProduct").and.callThrough();
            spyOn(productShippingPointsServiceMock, "getByProduct").and.callThrough();
            spyOn(productShippingPointsServiceMock, "deleteShippingPoint").and.callThrough();
            spyOn(productShippingPointsServiceMock, "saveShippingPoint").and.callThrough();
            spyOn(sippingPointsServiceMock, "searchDepartureShippingPointsByCoordinates").and.callThrough();
            spyOn(usersServiceMock, "getMe").and.callThrough();

            ItemsShippingCtrl = $controller('ItemsShippingCtrl', { $scope: scope, $stateParams: stateParams, $timeout: timeout,
                Endpoints: endpointsMock, ProductsService: productsServiceMock, ProductShippingPointsService: productShippingPointsServiceMock,
                ShippingPointsService: sippingPointsServiceMock, UsersService: usersServiceMock});
        }));

        it("ItemsShippingCtrl should be not null", function () {
            expect(!!ItemsShippingCtrl).toBe(true);
        });

        it("ItemsShippingCtrl:makeInitialSearchByAddress", function () {
            scope.makeInitialSearchByAddress();
        });

        it("ItemsShippingCtrl:fillInSchedule", function () {
            scope.fillInSchedule();
        });

        it("ItemsShippingCtrl:filterTime", function () {
            var timeStr = "12:12:12";
            scope.filterTime(timeStr);
        });

        it("ItemsShippingCtrl:showMapPointList", function () {
            scope.showMapPointList();
        });

        it("ItemsShippingCtrl:showMapPointDetails", function () {
            scope.showMapPointDetails();
        });

        it("ItemsShippingCtrl:showWellcomeScreen", function () {
            scope.showWellcomeScreen();
        });

        it("ItemsShippingCtrl:saveMapPoint", function () {
            scope.saveMapPoint();
        });

        it("ItemsShippingCtrl:savePoint", function () {
            scope.savePoint();
        });

        it("ItemsShippingCtrl:pointSelected", function () {
            scope.pointSelected();
        });

        it("ItemsShippingCtrl:cancelPointSelection", function () {
            scope.cancelPointSelection();
        });

        it("ItemsShippingCtrl:removeMapPoint", function () {
            scope.removeMapPoint();
        });

        it("ItemsShippingCtrl:searchShippingPoints", function () {
            scope.searchShippingPoints();
        });

        it("ItemsShippingCtrl:applyProductDetails", function () {
            scope.showPointList = true;
            var product = {
                address: {
                    city: "Paris",
                    street: "Champs"
                }
            };
            scope.applyProductDetails(product);
            expect(scope.addressQuery).toEqual(product.address.street + ", " + product.address.city);
        });

        it("ItemsShippingCtrl:applyProductShippingPoints", function () {
            var data = {
                results: [
                    {
                        opening_dates: [
                            {
                                day_of_week: "",
                                morning_opening_time: "",
                                morning_closing_time: "",
                                afternoon_opening_time: "",
                                afternoon_closing_time: ""
                            }
                        ]
                    }
                ]
            };
            scope.applyProductShippingPoints(data);
            expect(scope.productShippingPoint).toEqual(data.results[0]);
            expect(scope.showPointDetails).toBeTruthy();
        });

        it("ItemsShippingCtrl:parseShippingPointResult", function () {
            var result = {};
            scope.parseShippingPointResult(result);
            expect(scope.productShippingPoint).toEqual(result);
        });
    });
});
