define(["angular-mocks", "eloue/controllers/items/ItemsTermsCtrl"], function () {

    describe("Controller: ItemsTermsCtrl", function () {

        var ItemsTermsCtrl,
            scope,
            stateParams,
            categoriesServiceMock,
            productsServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            categoriesServiceMock = {
                getParentCategory: function (category) {
                    console.log("categoriesServiceMock:getParentCategory called with category = " + category);
                    return simpleServiceResponse;
                }
            };
            productsServiceMock = {
                getProductDetails: function (id) {
                    console.log("productsServiceMock:getProductDetails called with id = " + id);
                    return simpleServiceResponse;
                }
            };

            module(function ($provide) {
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("ProductsService", productsServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.markListItemAsSelected = function(){};
            scope.initCustomScrollbars = function(){};
            stateParams = {
                id: 1
            };

            spyOn(productsServiceMock, "getProductDetails").and.callThrough();
            spyOn(categoriesServiceMock, "getParentCategory").and.callThrough();

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

        it("ItemsTermsCtrl:applyProductDetails", function () {
            var product = {
                owner: {
                    is_professional: true
                },
                category: {
                    id: 2
                }
            };
            scope.applyProductDetails(product);
            expect(scope.isProfessional).toBeTruthy();
            expect(categoriesServiceMock.getParentCategory).toHaveBeenCalled();
        });
    });
});