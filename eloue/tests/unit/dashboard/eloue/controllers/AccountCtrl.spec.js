define(["angular-mocks", "eloue/controllers/AccountCtrl"], function() {

    describe("Controller: AccountCtrl", function () {

        var AccountCtrl,
            scope,
            state,
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

        beforeEach(inject(function ($rootScope, $state, $controller) {
            scope = $rootScope.$new();
            state = $state;

            spyOn(usersServiceMock, "getMe").and.callThrough();

            AccountCtrl = $controller('AccountCtrl', { $scope: scope, $state: state, UsersService: usersServiceMock });
            expect(usersServiceMock.getMe).toHaveBeenCalled();
        }));

        it("AccountCtrl should be not null", function () {
            expect(!!AccountCtrl).toBe(true);
        });
    });
});