define(["angular-mocks", "eloue/controllers/account/AccountPasswordCtrl"], function() {

    describe("Controller: AccountPasswordCtrl", function () {

        var AccountPasswordCtrl,
            scope,
            usersServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            usersServiceMock = {
                resetPassword: function (userId, form) {
                    console.log("usersServiceMock:resetPassword called with userId = " + userId + ", form = " + form);
                }
            };

            module(function($provide) {
                $provide.value("UsersService", usersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(usersServiceMock, "resetPassword").andCallThrough();

            AccountPasswordCtrl = $controller('AccountPasswordCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("AccountPasswordCtrl should be not null", function () {
            expect(!!AccountPasswordCtrl).toBe(true);
        });

        it("AccountPasswordCtrl:resetPassword", function () {
            scope.currentUser = { id: 1 };
            scope.resetPassword();
            expect(usersServiceMock.resetPassword).toHaveBeenCalled();
        });
    });
});