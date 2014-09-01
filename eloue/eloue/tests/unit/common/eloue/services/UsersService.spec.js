define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: UsersService", function () {

        var UsersService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_UsersService_) {
            UsersService = _UsersService_;
        }));

        it("UsersService should be not null", function () {
            expect(!!UsersService).toBe(true);
        });
    });
});
