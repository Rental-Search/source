define(["angular-mocks", "eloue/controllers/BookingsCtrl"], function() {

    describe("Controller: BookingsCtrl", function () {

        var BookingsCtrl,
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

            BookingsCtrl = $controller('BookingsCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("BookingsCtrl should be not null", function () {
            expect(!!BookingsCtrl).toBe(true);
        });
    });
});