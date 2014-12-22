define(["angular-mocks", "eloue/services/PhoneNumbersService"], function () {

    describe("Service: PhoneNumbersService", function () {

        var PhoneNumbersService,
            phoneNumbersMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            phoneNumbersMock = {
                save: function () {
                },
                update: function () {
                },
                getPremiumRateNumber: function() {}
            };

            module(function ($provide) {
                $provide.value("PhoneNumbers", phoneNumbersMock);
            });
        });

        beforeEach(inject(function (_PhoneNumbersService_) {
            PhoneNumbersService = _PhoneNumbersService_;
            spyOn(phoneNumbersMock, "save").and.callThrough();
            spyOn(phoneNumbersMock, "update").and.callThrough();
            spyOn(phoneNumbersMock, "getPremiumRateNumber").and.callThrough();
        }));

        it("PhoneNumbersService should be not null", function () {
            expect(!!PhoneNumbersService).toBe(true);
        });

        it("PhoneNumbersService:savePhoneNumber", function () {
            var phoneNumber = {};
            PhoneNumbersService.savePhoneNumber(phoneNumber);
            expect(phoneNumbersMock.save).toHaveBeenCalledWith(phoneNumber);
        });

        it("PhoneNumbersService:updatePhoneNumber", function () {
            var phoneNumbersId = 1;
            PhoneNumbersService.updatePhoneNumber({id: phoneNumbersId});
            expect(phoneNumbersMock.update).toHaveBeenCalledWith({id: phoneNumbersId}, {id: phoneNumbersId});
        });

        it("PhoneNumbersService:getPremiumRateNumber", function () {
            var phoneNumberId = 1;
            PhoneNumbersService.getPremiumRateNumber(phoneNumberId);
            expect(phoneNumbersMock.getPremiumRateNumber).toHaveBeenCalledWith({id: phoneNumberId, _cache: jasmine.any(Number)});
        });
    });
});