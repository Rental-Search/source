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
            serviceErrorsMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            authServiceMock = {
                login: function () {
                    console.log("Auth service mock called");
                },

                getUserToken: function () {
                    return "";
                },

                redirectToAttemptedUrl: function () {
                }
            };

            usersServiceMock = {
                getMe: function () {
                    return simpleServiceResponse;
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
            spyOn(authServiceMock, "getUserToken").and.callThrough();
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
            expect(document.cookie).toEqual("user_token=" + data.access_token);
        });

        it("LoginCtrl:onLoginError", function () {
            var jqXHR = {
                status: 400,
                responseJSON: {
                    error: "user_inactive"
                }
            };
            scope.onLoginError(jqXHR);
            expect(scope.inactiveUserError).toEqual("Cliquez ici pour recevoir le lien d'activation.");
        });

        it("LoginCtrl:authorize", function () {
            scope.authorize();
            expect(authServiceMock.getUserToken).toHaveBeenCalled();
        });
    });
});
