define(["angular-mocks", "eloue/controllers/DashboardRootCtrl"], function() {

    describe("Controller: DashboardRootCtrl", function () {

        var DashboardRootCtrl,
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

            DashboardRootCtrl = $controller('DashboardRootCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("DashboardRootCtrl should be not null", function () {
            expect(!!DashboardRootCtrl).toBe(true);
        });
    });
});