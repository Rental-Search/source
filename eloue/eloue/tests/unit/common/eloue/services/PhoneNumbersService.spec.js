define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: PhoneNumbersService", function () {

        var PhoneNumbersService,
            phoneNumbersMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            phoneNumbersMock = {
                get: function () {
                },
                update: function () {
                }
            };

            module(function ($provide) {
                $provide.value("PhoneNumbers", phoneNumbersMock);
            });
        });

        beforeEach(inject(function (_PhoneNumbersService_) {
            PhoneNumbersService = _PhoneNumbersService_;
            spyOn(phoneNumbersMock, "get").andCallThrough();
            spyOn(phoneNumbersMock, "update").andCallThrough();
        }));

        it("PhoneNumbersService should be not null", function () {
            expect(!!PhoneNumbersService).toBe(true);
        });
    });
});