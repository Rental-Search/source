define(["angular-mocks", "eloue/controllers/items/ItemsTariffsCtrl"], function() {

    describe("Controller: ItemsTariffsCtrl", function () {

        var ItemsTariffsCtrl,
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

            ItemsTariffsCtrl = $controller('ItemsTariffsCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("ItemsTariffsCtrl should be not null", function () {
            expect(!!ItemsTariffsCtrl).toBe(true);
        });
    });
});