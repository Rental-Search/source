define(["angular-mocks", "eloue/commonApp", "eloue/controllers"], function () {

    describe("Controller: ModalCtrl", function () {

        var ModalCtrl,
            scope,
            rootScope,
            route,
            location,
            timeout,
            authServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            authServiceMock = {};

            module(function ($provide) {
                $provide.value("AuthService", authServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            rootScope = $rootScope.$new();
            route = {};
            location = {};
            timeout = {};

            ModalCtrl = $controller('ModalCtrl', { $scope: scope, $rootScope: rootScope, $route: route, $location: location, $timeout: timeout, AuthService: authServiceMock});
        }));
    });
});
