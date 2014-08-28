define(["angular-mocks", "eloue/controllers/account/AccountProfileCtrl"], function() {

    describe("Controller: AccountProfileCtrl", function () {

        var AccountProfileCtrl,
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

            AccountProfileCtrl = $controller('AccountProfileCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("AccountProfileCtrl should be not null", function () {
            expect(!!AccountProfileCtrl).toBe(true);
        });
    });
});