define(["angular-mocks", "eloue/controllers/ItemsCtrl"], function () {

    describe("Controller: ItemsCtrl", function () {

        var ItemsCtrl,
            scope,
            productsServiceMock,
            usersServiceMock,
            categoriesServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            productsServiceMock = {
                getProductsByOwnerAndRootCategory: function (userId, rootCategoryId) {
                    console.log("productsServiceMock:getProductsByOwnerAndRootCategory called with userId = " + userId + ", rootCategoryId = " + rootCategoryId);
                    return {then: function () {
                        return {response: {}}
                    }}
                }
            };
            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return { id: 1190};
                }
            };
            categoriesServiceMock = {
                getRootCategories: function () {
                    console.log("categoriesServiceMock:getRootCategories called");
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };

            module(function ($provide) {
                $provide.value("ProductsService", productsServiceMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("CategoriesService", categoriesServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            scope.currentUser = {
                id: 1190
            };
            spyOn(usersServiceMock, "getMe").andCallThrough();

            spyOn(categoriesServiceMock, "getRootCategories").andCallThrough();
            spyOn(productsServiceMock, "getProductsByOwnerAndRootCategory").andCallThrough();

            ItemsCtrl = $controller('ItemsCtrl', { $scope: scope, ProductsService: productsServiceMock, UsersService: usersServiceMock, CategoriesService: categoriesServiceMock });
            expect(usersServiceMock.getMe).toHaveBeenCalled();
            expect(categoriesServiceMock.getRootCategories).toHaveBeenCalled();
        }));

        it("ItemsCtrl should be not null", function () {
            expect(!!ItemsCtrl).toBe(true);
        });

        it('ItemsCtrl:filterByCategory', function () {
            scope.selectedCategory = "Automobile";
            scope.filterByCategory();
            expect(productsServiceMock.getProductsByOwnerAndRootCategory).toHaveBeenCalledWith(1190, scope.selectedCategory);
        });
    });
});