define(["angular-mocks", "eloue/controllers/LoginCtrl"], function() {

    describe("Controller: LoginCtrl", function () {

        var LoginCtrl,
            scope,
            authServiceMock;

        beforeEach(module('EloueApp'));

        beforeEach(function () {
            authServiceMock = {login: function () {
                console.log("Auth service mock called");
            }};

            module(function($provide) {
                $provide.value("AuthService", authServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(authServiceMock, "login").andCallThrough();

            LoginCtrl = $controller('LoginCtrl', { $scope:scope, AuthService: authServiceMock});
        }));

        it('should make a call to authService', function () {
            scope.login();
            expect(authServiceMock.login).toHaveBeenCalled();
        });
    });
});
