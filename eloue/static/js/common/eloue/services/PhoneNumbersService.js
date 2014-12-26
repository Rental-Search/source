define(["../../../common/eloue/commonApp", "../../../common/eloue/resources"], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing phone numbers.
     */
    EloueCommon.factory("PhoneNumbersService", ["PhoneNumbers", function (PhoneNumbers) {
        var phoneNumbersService = {};

        phoneNumbersService.savePhoneNumber = function (phoneNumber) {
            return PhoneNumbers.save(phoneNumber).$promise;
        };

        phoneNumbersService.updatePhoneNumber = function (phoneNumber) {
            return PhoneNumbers.update({id: phoneNumber.id}, phoneNumber).$promise;
        };

        phoneNumbersService.getPremiumRateNumber = function (phoneNumberId) {
            return PhoneNumbers.getPremiumRateNumber({id: phoneNumberId, _cache: new Date().getTime()}).$promise;
        };

        return phoneNumbersService;
    }]);
});
