define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: PhoneNumbersService", function () {

        var PhoneNumbersService;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            module(function ($provide) {
            });
        });

        beforeEach(inject(function (_PhoneNumbersService_) {
            PhoneNumbersService = _PhoneNumbersService_;
        }));

        it("PhoneNumbersService should be not null", function () {
            expect(!!PhoneNumbersService).toBe(true);
        });
    });
});