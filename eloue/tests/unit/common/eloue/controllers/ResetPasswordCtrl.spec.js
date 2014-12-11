define(["angular-mocks", "eloue/commonApp", "eloue/controllers"], function () {

    describe("Controller: ResetPasswordCtrl", function () {

        var ResetPasswordCtrl,
            scope,
            window,
            authServiceMock,
            serviceErrorsMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            authServiceMock = {
                sendResetPasswordRequest: function (form, successCallback, errorCallback) {},

            };
            serviceErrorsMock = {};

            module(function ($provide) {
                $provide.value("AuthService", authServiceMock);
                $provide.value("ServiceErrors", serviceErrorsMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            window = {location:{}};

            ResetPasswordCtrl = $controller("ResetPasswordCtrl", { $scope: scope, $window: window, AuthService: authServiceMock, ServiceErrors: serviceErrorsMock});
        }));
    });
});
