define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ServerValidationService", function () {

        var ServerValidationService;

        beforeEach(module("EloueCommon"));

        beforeEach(inject(function (_ServerValidationService_) {
            ServerValidationService = _ServerValidationService_;
        }));

        it("ServerValidationService should be not null", function () {
            expect(!!ServerValidationService).toBe(true);
        });

        it("ServerValidationService:addErrors", function () {
            var messageError= "msg", description = "desc", fieldErrors = "", formTag = null;
            ServerValidationService.addErrors(messageError, description, fieldErrors, formTag);
        });

        it("ServerValidationService:removeErrors", function () {
            var formTag = null;
            ServerValidationService.removeErrors(formTag);
        });

        it("ServerValidationService:getFormErrorMessage", function () {
            var formTag = null;
            ServerValidationService.getFormErrorMessage(formTag);
        });

        it("ServerValidationService:getFormErrorMessage", function () {
            var fieldName = "", formTag = null;
            ServerValidationService.getFieldError(fieldName, formTag);
        });

        it("ServerValidationService:getErrors", function () {
            var formTag = null;
            ServerValidationService.getErrors(formTag);
        });

        it("ServerValidationService:addError", function () {
            var field, message, formTag = null;
            ServerValidationService.addError(field, message, formTag);
        });
    });
});