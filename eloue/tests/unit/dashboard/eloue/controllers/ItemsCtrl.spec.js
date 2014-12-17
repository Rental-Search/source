define(["angular-mocks", "eloue/controllers/ItemsCtrl"], function () {

    describe("Controller: ItemsCtrl", function () {

        var ItemsCtrl,
            scope,
            timeout,
            categoriesServiceMock,
            usersServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            categoriesServiceMock = {
                getRootCategories: function () {
                    console.log("categoriesServiceMock:getRootCategories called");
                    return {then: function () {
                        return {result: {}}
                    }}
                }
            };

            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };

            module(function ($provide) {
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("UsersService", usersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $timeout, $controller) {
            scope = $rootScope.$new();
            timeout = $timeout;
            scope.currentUserPromise = {
                then: function () {
                    return {result: {}}
                }
            };
            scope.currentUser = {
                id: 1190
            };

            spyOn(categoriesServiceMock, "getRootCategories").and.callThrough();
            spyOn(usersServiceMock, "getMe").and.callThrough();
            spyOn(scope, "$broadcast").and.callThrough();

            ItemsCtrl = $controller('ItemsCtrl', { $scope: scope, $timeout: timeout, CategoriesService: categoriesServiceMock, UsersService: usersServiceMock });
            expect(categoriesServiceMock.getRootCategories).toHaveBeenCalled();
        }));

        it("ItemsCtrl should be not null", function () {
            expect(!!ItemsCtrl).toBe(true);
        });

        it('ItemsCtrl:filterByCategory', function () {
            scope.selectedCategory = "Automobile";
            scope.filterByCategory();
            expect(scope.$broadcast).toHaveBeenCalledWith("startLoading", {
                parameters: [scope.currentUser.id, scope.selectedCategory],
                shouldReloadList: true
            });
        });
    });
});