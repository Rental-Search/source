define(["angular-mocks", "eloue/controllers/RegisterCtrl"], function () {

    describe("Controller: RegisterCtrl", function () {

        var RegisterCtrl,
            scope,
            rootScope,
            http,
            window,
            authServiceMock,
            civilityChoicesMock,
            usersServiceMock,
            serviceErrorsMock,
            redirectAfterLoginMock,
            toDashboardRedirectServiceMock,
            serverValidationServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            authServiceMock = {
                register: function () {
                    console.log("Auth service mock called");
                    return {
                        $promise: {
                            then: function () {
                                return {response: {}}
                            }
                        }
                    }
                },

                clearUserData: function () {

                },

                login: function (credentials, successCallback, errorCallback) {

                },

                getUserToken: function () {
                    return "";
                },

                redirectToAttemptedUrl: function () {
                }
            };

            civilityChoicesMock = {};

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

            redirectAfterLoginMock = {
                url: ""
            };

            toDashboardRedirectServiceMock = {
                showPopupAndRedirect: function (href) {
                }
            };

            serverValidationServiceMock = {
                removeErrors: function () {
                },
                addError: function (field, message, formTag) {
                }
            };

            module(function ($provide) {
                $provide.value("AuthService", authServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller, $httpBackend) {
            scope = $rootScope.$new();
            http = $httpBackend;
            http.defaults = {};

            spyOn(authServiceMock, "register").and.callThrough();
            spyOn(authServiceMock, "clearUserData").and.callThrough();
            spyOn(authServiceMock, "login").and.callThrough();
            spyOn(authServiceMock, "getUserToken").and.callThrough();
            spyOn(authServiceMock, "redirectToAttemptedUrl").and.callThrough();
            spyOn(usersServiceMock, "getMe").and.callThrough();
            spyOn(toDashboardRedirectServiceMock, "showPopupAndRedirect").and.callThrough();
            spyOn(serverValidationServiceMock, "removeErrors").and.callThrough();
            spyOn(serverValidationServiceMock, "addError").and.callThrough();

            RegisterCtrl = $controller("RegisterCtrl", {
                $scope: scope,
                $rootScope: rootScope,
                $http: http,
                $window: window,
                AuthService: authServiceMock,
                CivilityChoices: civilityChoicesMock,
                UsersService: usersServiceMock,
                ServiceErrors: serviceErrorsMock,
                RedirectAfterLogin: redirectAfterLoginMock,
                ToDashboardRedirectService: toDashboardRedirectServiceMock,
                ServerValidationService: serverValidationServiceMock
            });
        }));

        it("RegisterCtrl:register", function () {
            scope.register();
            expect(authServiceMock.register).toHaveBeenCalled();
        });

        it("RegisterCtrl:getEventLabel", function () {
            scope.getEventLabel();
        });

        it("RegisterCtrl:onLoginSuccess", function () {
            var data = {
                access_token: "token"
            };
            scope.onLoginSuccess(data);
        });

        it("RegisterCtrl:onLoginError", function () {
            var jqXHR = {};
            scope.onLoginError(jqXHR);
        });

        it("RegisterCtrl:openRegistrationForm", function () {
            scope.openRegistrationForm();
        });

        it("RegisterCtrl:authorize", function () {
            scope.authorize();
        });
    });
});