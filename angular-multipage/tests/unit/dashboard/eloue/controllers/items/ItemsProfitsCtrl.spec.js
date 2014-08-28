define(["angular-mocks", "eloue/controllers/items/ItemsProfitsCtrl"], function() {

    describe("Controller: ItemsProfitsCtrl", function () {

        var ItemsProfitsCtrl,
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

            ItemsProfitsCtrl = $controller('ItemsProfitsCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("ItemsProfitsCtrl should be not null", function () {
            expect(!!ItemsProfitsCtrl).toBe(true);
        });
    });
});