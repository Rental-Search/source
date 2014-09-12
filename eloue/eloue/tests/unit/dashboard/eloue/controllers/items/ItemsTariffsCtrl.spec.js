define(["angular-mocks", "eloue/controllers/items/ItemsTariffsCtrl"], function () {

    describe("Controller: ItemsTariffsCtrl", function () {

        var ItemsTariffsCtrl,
            scope,
            stateParams,
            endpointsMock,
            currencyMock,
            unitMock,
            categoriesServiceMock,
            productsServiceMock,
            pricesServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            categoriesServiceMock = {
                getParentCategory: function (category) {
                    console.log("categoriesServiceMock:getParentCategory called with category = " + category);
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };
            productsServiceMock = {
                getProductDetails: function (id) {
                    console.log("productsServiceMock:getProductDetails called with id = " + id);
                    return {then: function () {
                        return {response: {}}
                    }}
                },
                updateProduct: function (product) {
                    console.log("productsServiceMock:updateProduct called with product = " + product);
                }
            };
            pricesServiceMock = {
                getPricesByProduct: function (productId) {
                    console.log("pricesServiceMock:getPricesByProduct called with productId = " + productId);
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                },
                updatePrice: function (price) {
                    console.log("pricesServiceMock:updatePrice called with price = " + price)
                },
                savePrice: function (price) {
                    console.log("pricesServiceMock:savePrice called with price = " + price)
                }
            };

            module(function ($provide) {
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("ProductsService", productsServiceMock);
                $provide.value("PricesService", pricesServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            stateParams = {
                id: 1
            };
            endpointsMock = {
                oauth_url: "http://10.0.5.47:8200/oauth2/",
                api_url: "http://10.0.5.47:8200/api/2.0/"
            };
            unitMock = {
                "HOUR": {id: 0, name: "heure", description: "1 heure"},
                "DAY": {id: 1, name: "", description: ""},
                "WEEK_END": {id: 2, name: "jour", description: "1 jour"},
                "WEEK": {id: 3, name: "semaine", description: "1 semaine"},
                "TWO_WEEKS": {id: 4, name: "deux semaines", description: "2 semaines"},
                "MONTH": {id: 5, name: "mois", description: "1 mois"},
                "THREE_DAYS": {id: 6, name: "3jours", description: "3 jours"},
                "FIFTEEN_DAYS": {id: 7, name: "15jours", description: "15 jours"}
            };
            currencyMock = {
                "EUR": {name: "EUR", symbol: "€"},
                "USD": {name: "USD", symbol: "$"},
                "GBP": {name: "GPB", symbol: "£"},
                "JPY": {name: "YEN", symbol: "¥"},
                "XPF": {name: "XPF", symbol: "F"}
            };

            spyOn(categoriesServiceMock, "getParentCategory").andCallThrough();
            spyOn(productsServiceMock, "getProductDetails").andCallThrough();
            spyOn(productsServiceMock, "updateProduct").andCallThrough();
            spyOn(pricesServiceMock, "getPricesByProduct").andCallThrough();
            spyOn(pricesServiceMock, "updatePrice").andCallThrough();
            spyOn(pricesServiceMock, "savePrice").andCallThrough();

            ItemsTariffsCtrl = $controller('ItemsTariffsCtrl', { $scope: scope, $stateParams: stateParams,
                Endpoints: endpointsMock, Currency: currencyMock, Unit: unitMock,
                CategoriesService: categoriesServiceMock, ProductsService: productsServiceMock,
                PricesService: pricesServiceMock });
            expect(productsServiceMock.getProductDetails).toHaveBeenCalledWith(stateParams.id);
            expect(pricesServiceMock.getPricesByProduct).toHaveBeenCalledWith(stateParams.id);
        }));

        it("ItemsTariffsCtrl should be not null", function () {
            expect(!!ItemsTariffsCtrl).toBe(true);
        });

        it("ItemsTariffsCtrl:updateFieldSet auto", function () {
            var category = {
                name: "Automobile"
            };
            scope.updateFieldSet(category);
            expect(scope.isAuto).toBe(true);
            expect(scope.isRealEstate).toBe(false);
        });

        it("ItemsTariffsCtrl:updateFieldSet real estate", function () {
            var category = {
                name: "Hébergement"
            };
            scope.updateFieldSet(category);
            expect(scope.isAuto).toBe(false);
            expect(scope.isRealEstate).toBe(true);
        });

        it("ItemsTariffsCtrl:updateFieldSet state", function () {
            var category = {
                name: "Bebe"
            };
            scope.updateFieldSet(category);
            expect(scope.isAuto).toBe(false);
            expect(scope.isRealEstate).toBe(false);
        });

        it("ItemsTariffsCtrl:updatePrices update price", function () {
            scope.product = {
                id: 1
            };
            scope.prices = [
                {id: 1}
            ];
            scope.updatePrices();
            expect(pricesServiceMock.updatePrice).toHaveBeenCalled();
        });

        it("ItemsTariffsCtrl:updatePrices save price", function () {
            scope.product = {
                id: 1
            };
            scope.prices = [
                {id: undefined}
            ];

            scope.updatePrices();
            expect(pricesServiceMock.savePrice).toHaveBeenCalled();
        });
    });
});