"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/resources"], function (EloueCommon) {
    /**
     * Service for managing phone numbers.
     */
    EloueCommon.factory("PhoneNumbersService", ["PhoneNumbers", function (PhoneNumbers) {
        var phoneNumbersService = {};

        phoneNumbersService.savePhoneNumber = function (phoneNumber) {
            return PhoneNumbers.save(phoneNumber);
        };

        phoneNumbersService.updatePhoneNumber = function (phoneNumber) {
            return PhoneNumbers.update({id: phoneNumber.id}, phoneNumber);
        };

        phoneNumbersService.getPremiumRateNumber = function (phoneNumberId) {
            return PhoneNumbers.getPremiumRateNumber({id: phoneNumberId, _cache: new Date().getTime()});
        };

        return phoneNumbersService;
    }]);
});
