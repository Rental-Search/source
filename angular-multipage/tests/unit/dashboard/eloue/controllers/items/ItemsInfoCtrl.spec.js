define(["angular-mocks", "eloue/controllers/items/ItemsInfoCtrl"], function() {

    describe("Controller: ItemsInfoCtrl", function () {

        var ItemsInfoCtrl,
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

            ItemsInfoCtrl = $controller('ItemsInfoCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("ItemsInfoCtrl should be not null", function () {
            expect(!!ItemsInfoCtrl).toBe(true);
        });
    });
});