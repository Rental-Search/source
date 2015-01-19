define(["angular-mocks", "eloue/controllers/DashboardCtrl"], function() {

    describe("Controller: DashboardCtrl", function () {

        var DashboardCtrl,
            scope,
            activityTypeMock,
            usersServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            activityTypeMock = {};
            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return simpleServiceResponse;
                }
            };

            module(function($provide) {
                $provide.value("ActivityType", activityTypeMock);
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
            spyOn(usersServiceMock, "getMe").and.callThrough();

            DashboardCtrl = $controller('DashboardCtrl', { $scope: scope, ActivityType: activityTypeMock, UsersService: usersServiceMock });
        }));

        it("DashboardCtrl should be not null", function () {
            expect(!!DashboardCtrl).toBe(true);
        });
    });
});