define(["angular-mocks", "eloue/commonApp", "eloue/controllers"], function () {

    describe("Controller: AuthCtrl", function () {

        var AuthCtrl,
            scope,
            window,
            authServiceMock,
            usersServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            authServiceMock = {clearUserData: function () {
                console.log("Auth service mock called");
            }};

            usersServiceMock = {
                getMe: function () {
                    console.log("Users service mock called");
                    return {$promise: {then: function () {
                        return {results: [
                            {}
                        ]}
                    }}}
                },
                getStatistics: function () {
                    console.log("Users service mock called");
                }
            };

            module(function ($provide) {
                $provide.value("AuthService", authServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            window = {location:{}};

            spyOn(authServiceMock, "clearUserData").and.callThrough();

            AuthCtrl = $controller('AuthCtrl', { $scope: scope, $window: window, AuthService: authServiceMock, UsersService: usersServiceMock});
        }));
    });
});
