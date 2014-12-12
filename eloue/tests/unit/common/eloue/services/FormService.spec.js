define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: FormService", function () {

        var FormService,
            serverValidationServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            serverValidationServiceMock = {
                addErrors: function(messageError, description, fieldErrors, formTag) {},
                removeErrors: function() {}
            };

            module(function ($provide) {
                $provide.value("ServerValidationService", serverValidationServiceMock);
            });
        });

        beforeEach(inject(function (_FormService_) {
            FormService = _FormService_;
            spyOn(serverValidationServiceMock, "addErrors").and.callThrough();
            spyOn(serverValidationServiceMock, "removeErrors").and.callThrough();
        }));

        it("FormService should be not null", function () {
            expect(!!FormService).toBe(true);
        });
    });
});
