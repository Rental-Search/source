define(["angular-mocks", "eloue/controllers/DashboardCtrl"], function() {

    describe("Controller: DashboardCtrl", function () {

        var DashboardCtrl,
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
            scope.currentUserPromise = {
                then: function () {
                }
            };
            scope.currentUser = { id: 1};
            spyOn(usersServiceMock, "getMe").andCallThrough();

            DashboardCtrl = $controller('DashboardCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("DashboardCtrl should be not null", function () {
            expect(!!DashboardCtrl).toBe(true);
        });
    });
});