define(["angular-mocks", "eloue/controllers/AuthCtrl"], function () {

    describe("Controller: AuthCtrl", function () {

        var AuthCtrl,
            scope,
            window,
            authServiceMock,
            usersServiceMock;

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
                    return {
                        $promise: {
                            then: function () {
                                return {
                                    results: [
                                        {}
                                    ]
                                }
                            }
                        }
                    }
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
