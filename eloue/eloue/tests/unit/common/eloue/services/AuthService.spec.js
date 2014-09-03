define(["angular-mocks", "eloue/commonApp", "eloue/services"], function() {

    describe("Service: AuthService", function () {

        var AuthService, endpointsMock, redirectAfterLoginMock, registrationResourceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            endpointsMock = {};
            redirectAfterLoginMock = {};
            registrationResourceMock = {
                "register": {

                }
            };

            module(function($provide) {
                $provide.value("Endpoints", endpointsMock);
                $provide.value("RedirectAfterLogin", redirectAfterLoginMock);
                $provide.value("Registration", registrationResourceMock);
            });
        });

        beforeEach(inject(function (_AuthService_) {
            AuthService = _AuthService_;
            AuthService.getCookie = function () {
                return "111";
            };
            AuthService.redirectToAttemptedUrl = function () {

            };
            spyOn(AuthService, "getCookie").andCallThrough();
            spyOn(AuthService, "redirectToAttemptedUrl").andCallThrough();
            spyOn(registrationResourceMock, "register").andCallThrough();
        }));

        it("AuthService should be not null", function() {
            expect(!!AuthService).toBe(true);
        });

        it("AuthService should have all functions", function() {
            expect(angular.isFunction(AuthService.login)).toBe(true);
            expect(angular.isFunction(AuthService.authorize)).toBe(true);
            expect(angular.isFunction(AuthService.clearUserData)).toBe(true);
            expect(angular.isFunction(AuthService.redirectToAttemptedUrl)).toBe(true);
            expect(angular.isFunction(AuthService.saveAttemptUrl)).toBe(true);
            expect(angular.isFunction(AuthService.register)).toBe(true);
            expect(angular.isFunction(AuthService.isLoggedIn)).toBe(true);
            expect(angular.isFunction(AuthService.getCookie)).toBe(true);
        });

        it("AuthService should make a call to itself", function () {
            var credentials = {};
            AuthService.login(credentials);
            expect(AuthService.getCookie).toHaveBeenCalledWith("user_token");
        });

        it("AuthService should make a call to itself", function () {
            var credentials = {};
            AuthService.authorize(credentials);
            expect(AuthService.getCookie).toHaveBeenCalledWith("user_token");
            expect(AuthService.redirectToAttemptedUrl).toHaveBeenCalledWith();
        });
    });
});