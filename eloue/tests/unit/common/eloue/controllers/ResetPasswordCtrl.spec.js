define(["angular-mocks", "eloue/controllers/ResetPasswordCtrl"], function () {

    describe("Controller: ResetPasswordCtrl", function () {

        var ResetPasswordCtrl,
            scope,
            window,
            authServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            authServiceMock = {
                sendResetPasswordRequest: function (form, successCallback, errorCallback) {}
            };

            module(function ($provide) {
                $provide.value("AuthService", authServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            window = {location:{}};

            ResetPasswordCtrl = $controller("ResetPasswordCtrl", { $scope: scope, $window: window, AuthService: authServiceMock});
        }));
    });
});
