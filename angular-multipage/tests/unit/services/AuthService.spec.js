define(["angular-mocks", "eloue/services/AuthService"], function() {

    describe("Service: AuthService", function () {

        var AuthService, usersResourceMock;

        beforeEach(module("EloueApp"));

        beforeEach(function () {
            usersResourceMock = {get: function () {
            }};

            module(function($provide) {
                $provide.value("Users", usersResourceMock);
            });
        });

        beforeEach(inject(function (_UserService_) {
            UserService = _UserService_;
            spyOn(usersResourceMock, "get").andCallThrough();
        }));

        it("UserService should be not null", function() {
            expect(!!UserService).toBe(true);
        });

        it("UserService should have a getUser function", function() {
            expect(angular.isFunction(UserService.getUser)).toBe(true);
        });

        it("UserService should make a call to Users resource", function () {
            UserService.getUser(1);
            expect(usersResourceMock.get).toHaveBeenCalledWith({id: 1});
        });
    });
});