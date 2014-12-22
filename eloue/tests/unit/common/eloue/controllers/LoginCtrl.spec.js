define(["angular-mocks", "eloue/controllers/LoginCtrl"], function () {

    describe("Controller: LoginCtrl", function () {

        var LoginCtrl,
            scope,
            rootScope,
            http,
            window,
            routeParams,
            authServiceMock,
            usersServiceMock,
            serviceErrorsMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            authServiceMock = {
                login: function () {
                    console.log("Auth service mock called");
                },

                getCookie: function (cname) {
                    return "";
                },

                redirectToAttemptedUrl: function () {
                }
            };

            usersServiceMock = {
                getMe: function () {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                }
            };

            serviceErrorsMock = {};

            module(function ($provide) {
                $provide.value("AuthService", authServiceMock);
                $provide.value("UsersService", usersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller, $httpBackend) {
            scope = $rootScope.$new();
            rootScope = $rootScope.$new();
            http = $httpBackend;
            http.defaults = {headers: {common: {authorization: ""}}};
            window = {};
            routeParams = {};

            spyOn(authServiceMock, "login").and.callThrough();
            spyOn(authServiceMock, "getCookie").and.callThrough();
            spyOn(authServiceMock, "redirectToAttemptedUrl").and.callThrough();
            spyOn(usersServiceMock, "getMe").and.callThrough();

            LoginCtrl = $controller("LoginCtrl", {
                $scope: scope,
                $rootScope: rootScope,
                $http: http,
                $window: window,
                $routeParams: routeParams,
                AuthService: authServiceMock,
                UsersService: usersServiceMock,
                ServiceErrors: serviceErrorsMock
            });
        }));

        it("LoginCtrl:login", function () {
            scope.login();
            expect(authServiceMock.login).toHaveBeenCalled();
        });

        it("LoginCtrl:onLoginSuccess", function () {
            var data = {
                access_token: "token"
            };
            scope.onLoginSuccess(data);
        });

        it("LoginCtrl:onLoginError", function () {
            var jqXHR = {};
            scope.onLoginError(jqXHR);
        });

        it("LoginCtrl:authorize", function () {
            scope.authorize();
        });
    });
});
