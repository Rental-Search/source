define(["angular-mocks", "eloue/controllers/ItemsCtrl"], function () {

    describe("Controller: ItemsCtrl", function () {

        var ItemsCtrl,
            scope,
            rootScope,
            categoriesServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            categoriesServiceMock = {
                getRootCategories: function () {
                    console.log("categoriesServiceMock:getRootCategories called");
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };

            module(function ($provide) {
                $provide.value("CategoriesService", categoriesServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            rootScope = $rootScope;
            scope.currentUserPromise = {
                then: function () {
                    return {result: {}}
                }
            };
            scope.currentUser = {
                id: 1190
            };

            spyOn(categoriesServiceMock, "getRootCategories").andCallThrough();

            ItemsCtrl = $controller('ItemsCtrl', { $scope: scope, $rootScope: rootScope, CategoriesService: categoriesServiceMock });
            expect(categoriesServiceMock.getRootCategories).toHaveBeenCalled();
        }));

        it("ItemsCtrl should be not null", function () {
            expect(!!ItemsCtrl).toBe(true);
        });

        it('ItemsCtrl:filterByCategory', function () {
            scope.selectedCategory = "Automobile";
            scope.filterByCategory();
        });
    });
});