define(["angular-mocks", "eloue/controllers/AuthCtrl"], function () {

    describe("Controller: AuthCtrl", function () {

        var AuthCtrl,
            scope,
            window,
            authServiceMock,
            usersServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            authServiceMock = {
                clearUserData: function () {
                    console.log("Auth service mock called");
                },
                getUserToken: function () {
                    return "U_token";
                }
            };

            usersServiceMock = {
                getMe: function () {
                    console.log("Users service mock called");
                    return simpleServiceResponse;
                },
                getStatistics: function () {
                    console.log("Users service mock called");
                    return simpleServiceResponse;
                }
            };

            module(function ($provide) {
                $provide.value("AuthService", authServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            window = {location: {
                href: "url",
                reload: function() {}
            }};

            spyOn(authServiceMock, "clearUserData").and.callThrough();

            AuthCtrl = $controller('AuthCtrl', {
                $scope: scope,
                $window: window,
                AuthService: authServiceMock,
                UsersService: usersServiceMock
            });
        }));

        it("AuthCtrl:logout", function () {
            scope.logout();
        });
    });
});
