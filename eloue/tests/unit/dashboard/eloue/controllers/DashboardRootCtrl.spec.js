define(["angular-mocks", "eloue/controllers/DashboardRootCtrl"], function() {

    describe("Controller: DashboardRootCtrl", function () {

        var DashboardRootCtrl,
            scope,
            usersServiceMock,
            authServiceMock;

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

            authServiceMock = {
                getCookie: function(name) {
                    return "token";
                }
            };

            module(function($provide) {
                $provide.value("UsersService", usersServiceMock);
                $provide.value("AuthService", authServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(usersServiceMock, "getMe").and.callThrough();
            spyOn(authServiceMock, "getCookie").and.callThrough();

            DashboardRootCtrl = $controller('DashboardRootCtrl', { $scope: scope, UsersService: usersServiceMock, AuthService: authServiceMock });
        }));

        it("DashboardRootCtrl should be not null", function () {
            expect(!!DashboardRootCtrl).toBe(true);
        });
    });
});