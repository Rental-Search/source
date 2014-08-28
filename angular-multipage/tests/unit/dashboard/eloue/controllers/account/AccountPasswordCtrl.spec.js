define(["angular-mocks", "eloue/controllers/account/AccountPasswordCtrl"], function() {

    describe("Controller: AccountPasswordCtrl", function () {

        var AccountPasswordCtrl,
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

            AccountPasswordCtrl = $controller('AccountPasswordCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("AccountPasswordCtrl should be not null", function () {
            expect(!!AccountPasswordCtrl).toBe(true);
        });
    });
});