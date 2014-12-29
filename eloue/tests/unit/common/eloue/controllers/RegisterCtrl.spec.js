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
            serverValidationServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            authServiceMock = {
                register: function () {
                    console.log("Auth service mock called");
                    return simpleServiceResponse;
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
                    return simpleServiceResponse;
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
            var result = scope.getEventLabel();
            expect(result).toEqual("Simple");

            redirectAfterLoginMock.url = "#booking";
            result = scope.getEventLabel();
            expect(result).toEqual("Réservation");

            redirectAfterLoginMock.url = "#message";
            result = scope.getEventLabel();
            expect(result).toEqual("Message");

            redirectAfterLoginMock.url = "#phone";
            result = scope.getEventLabel();
            expect(result).toEqual("Appel");

            redirectAfterLoginMock.url = "#publish";
            result = scope.getEventLabel();
            expect(result).toEqual("Dépôt annonce");
        });

        it("RegisterCtrl:onLoginSuccess", function () {
            var data = {
                access_token: "token"
            };
            scope.onLoginSuccess(data);
            expect(document.cookie).toEqual("user_token=" + data.access_token);
        });

        it("RegisterCtrl:onLoginError", function () {
            var jqXHR = {
                status: 400,
                responseJSON: {
                    error: "user_inactive"
                }
            };
            scope.onLoginError(jqXHR);
            expect(scope.loginError).toEqual("Bad request.");
        });

        it("RegisterCtrl:openRegistrationForm", function () {
            scope.openRegistrationForm();
        });

        it("RegisterCtrl:authorize", function () {
            scope.authorize();
            expect(authServiceMock.getUserToken).toHaveBeenCalled();
        });
    });
});