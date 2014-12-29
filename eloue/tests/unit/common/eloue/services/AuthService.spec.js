define(["angular-mocks", "eloue/services/AuthService"], function() {

    describe("Service: AuthService", function () {

        var AuthService, q, rootScope, window, document, formServiceMock,
            endpointsMock, authConstantsMock, redirectAfterLoginMock, registrationResourceMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            endpointsMock = {};
            authConstantsMock = {};
            redirectAfterLoginMock = {};
            registrationResourceMock = {
                register: function() {
                    return simpleResourceResponse;
                }
            };

            module(function($provide) {
                $provide.value("Endpoints", endpointsMock);
                $provide.value("AuthConstants", authConstantsMock);
                $provide.value("RedirectAfterLogin", redirectAfterLoginMock);
                $provide.value("Registration", registrationResourceMock);
            });
        });

        beforeEach(inject(function (_AuthService_, $q, $rootScope, $window, $document) {
            AuthService = _AuthService_;
            q = $q; rootScope = $rootScope; window = $window; document = $document;
            AuthService.getCookie = function () {
                return "111";
            };
            AuthService.redirectToAttemptedUrl = function () {};
            spyOn(AuthService, "getCookie").and.callThrough();
            spyOn(AuthService, "redirectToAttemptedUrl").and.callThrough();
            spyOn(registrationResourceMock, "register").and.callThrough();
        }));

        it("AuthService should be not null", function() {
            expect(!!AuthService).toBe(true);
        });

        it("AuthService should have all functions", function() {
            expect(angular.isFunction(AuthService.login)).toBe(true);
            expect(angular.isFunction(AuthService.clearUserData)).toBe(true);
            expect(angular.isFunction(AuthService.redirectToAttemptedUrl)).toBe(true);
            expect(angular.isFunction(AuthService.saveAttemptUrl)).toBe(true);
            expect(angular.isFunction(AuthService.register)).toBe(true);
            expect(angular.isFunction(AuthService.isLoggedIn)).toBe(true);
            expect(angular.isFunction(AuthService.getCookie)).toBe(true);
        });

        it("AuthService:login", function () {
            var credentials = {};
            AuthService.login(credentials);
        });

        it("AuthService:loginFacebook", function () {
            var url = "";
            AuthService.loginFacebook(url);
        });

        it("AuthService:clearUserData", function () {
            AuthService.clearUserData();
        });

        it("AuthService:redirectToAttemptedUrl", function () {
            AuthService.redirectToAttemptedUrl();
        });

        it("AuthService:saveAttemptUrl", function () {
            AuthService.saveAttemptUrl();
        });

        it("AuthService:sendActivationLink", function () {
            AuthService.sendActivationLink();
        });

        it("AuthService:register", function () {
            AuthService.register();
            expect(registrationResourceMock.register).toHaveBeenCalled();
        });
        it("AuthService:isLoggedIn", function () {
            AuthService.isLoggedIn();
        });

        it("AuthService:getCookie", function () {
            AuthService.getCookie();
        });

        it("AuthService:getUserToken", function () {
            AuthService.getUserToken();
        });

        it("AuthService:getCSRFToken", function () {
            AuthService.getCSRFToken();
        });
    });
});