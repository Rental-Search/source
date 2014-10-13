define(["angular-mocks", "eloue/controllers/items/ItemsTermsCtrl"], function () {

    describe("Controller: ItemsTermsCtrl", function () {

        var ItemsTermsCtrl,
            scope,
            stateParams,
            categoriesServiceMock,
            productsServiceMock;

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
                }
            };

            module(function ($provide) {
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("ProductsService", productsServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            stateParams = {
                id: 1
            };

            spyOn(productsServiceMock, "getProductDetails").andCallThrough();
            spyOn(categoriesServiceMock, "getParentCategory").andCallThrough();

            ItemsTermsCtrl = $controller('ItemsTermsCtrl', { $scope: scope, $stateParams: stateParams, CategoriesService: categoriesServiceMock, ProductsService: productsServiceMock });
            expect(productsServiceMock.getProductDetails).toHaveBeenCalledWith(stateParams.id);
        }));

        it("ItemsTermsCtrl should be not null", function () {
            expect(!!ItemsTermsCtrl).toBe(true);
        });

        it("ItemsTermsCtrl:updateTermsBlocks auto", function () {
            var category = {
                name: "Automobile"
            };
            scope.updateTermsBlocks(category);
            expect(scope.isAuto).toBe(true);
            expect(scope.isRealEstate).toBe(false);
        });

        it("ItemsTermsCtrl:updateTermsBlocks real estate", function () {
            var category = {
                name: "Location saisonnière"
            };
            scope.updateTermsBlocks(category);
            expect(scope.isAuto).toBe(false);
            expect(scope.isRealEstate).toBe(true);
        });

        it("ItemsTermsCtrl:updateTermsBlocks simple", function () {
            var category = {
                name: "Bebe"
            };
            scope.updateTermsBlocks(category);
            expect(scope.isAuto).toBe(false);
            expect(scope.isRealEstate).toBe(false);
        });
    });
});