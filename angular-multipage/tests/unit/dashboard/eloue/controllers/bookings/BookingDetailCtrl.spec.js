define(["angular-mocks", "eloue/controllers/bookings/BookingDetailCtrl"], function() {

    describe("Controller: BookingDetailCtrl", function () {

        var BookingDetailCtrl,
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

            BookingDetailCtrl = $controller('BookingDetailCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("BookingDetailCtrl should be not null", function () {
            expect(!!BookingDetailCtrl).toBe(true);
        });
    });
});