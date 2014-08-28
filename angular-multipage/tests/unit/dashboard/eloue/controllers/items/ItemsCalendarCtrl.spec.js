define(["angular-mocks", "eloue/controllers/items/ItemsCalendarCtrl"], function() {

    describe("Controller: ItemsCalendarCtrl", function () {

        var ItemsCalendarCtrl,
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

            ItemsCalendarCtrl = $controller('ItemsCalendarCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("ItemsCalendarCtrl should be not null", function () {
            expect(!!ItemsCalendarCtrl).toBe(true);
        });
    });
});