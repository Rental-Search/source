define(["angular-mocks", "eloue/controllers/AccountCtrl"], function() {

    describe("Controller: AccountCtrl", function () {

        var AccountCtrl,
            scope,
            usersServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };

            module(function($provide) {
                $provide.value("UsersService", usersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(usersServiceMock, "getMe").andCallThrough();

            AccountCtrl = $controller('AccountCtrl', { $scope: scope, UsersService: usersServiceMock });
            expect(usersServiceMock.getMe).toHaveBeenCalled();
        }));

        it("AccountCtrl should be not null", function () {
            expect(!!AccountCtrl).toBe(true);
        });
    });
});