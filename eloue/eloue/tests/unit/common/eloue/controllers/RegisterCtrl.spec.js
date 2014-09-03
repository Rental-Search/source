define(["angular-mocks", "eloue/commonApp", "eloue/controllers"], function() {

    describe("Controller: RegisterCtrl", function () {

        var RegisterCtrl,
            scope,
            authServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            authServiceMock = {register: function () {
                console.log("Auth service mock called");
                return {$promise: {then: function () {
                    return {response: {}}
                }}}
            }};

            module(function($provide) {
                $provide.value("AuthService", authServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(authServiceMock, "register").andCallThrough();

            RegisterCtrl = $controller('RegisterCtrl', { $scope:scope, AuthService: authServiceMock});
        }));

        it('should make a call to Auth service', function () {
            scope.register();
            expect(authServiceMock.register).toHaveBeenCalled();
        });
    });
});