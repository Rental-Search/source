define(["angular-mocks", "eloue/controllers/DashboardRootCtrl"], function() {

    describe("Controller: DashboardRootCtrl", function () {

        var DashboardRootCtrl,
            scope,
            usersServiceMock,
            authServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return simpleServiceResponse;
                },

                getStatistics: function (userId) {
                    return simpleServiceResponse;
                }
            };

            authServiceMock = {
                getUserToken: function() {
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
            spyOn(usersServiceMock, "getStatistics").and.callThrough();
            spyOn(authServiceMock, "getUserToken").and.callThrough();

            DashboardRootCtrl = $controller('DashboardRootCtrl', { $scope: scope, UsersService: usersServiceMock, AuthService: authServiceMock });
        }));

        it("DashboardRootCtrl should be not null", function () {
            expect(!!DashboardRootCtrl).toBe(true);
        });

        it("DashboardRootCtrl:updateStatistics", function () {
            scope.currentUser = {
                id: 1
            };
            scope.updateStatistics();
        });

        it("DashboardRootCtrl:clearSelectedItem", function () {
            scope.clearSelectedItem();
        });

        it("DashboardRootCtrl:isItemSelected", function () {
            scope.isItemSelected();
        });

        it("DashboardRootCtrl:markListItemAsSelected", function () {
            scope.markListItemAsSelected();
        });

        it("DashboardRootCtrl:initCustomScrollbars", function () {
            scope.initCustomScrollbars();
        });

        it("DashboardRootCtrl:showNotification", function () {
            scope.showNotification();
        });
    });
});