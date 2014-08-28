define(["angular-mocks", "eloue/controllers/items/ItemsTabsCtrl"], function() {

    describe("Controller: ItemsTabsCtrl", function () {

        var ItemsTabsCtrl,
            scope,
            usersServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return { id: 1190};
                }
            };

            module(function($provide) {
                $provide.value("UsersService", usersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(usersServiceMock, "getMe").andCallThrough();

            ItemsTabsCtrl = $controller('ItemsTabsCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("ItemsTabsCtrl should be not null", function () {
            expect(!!ItemsTabsCtrl).toBe(true);
        });
    });
});