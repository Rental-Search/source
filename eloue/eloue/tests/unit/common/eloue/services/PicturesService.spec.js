define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: PicturesService", function () {

        var PicturesService,
            picturesMock,
            endpointsMock,
            formServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            picturesMock = {
                get: function () {
                }
            };
            endpointsMock = {

            };
            formServiceMock = {
                send: function (method, url, form, successCallback, errorCallback) {
                }
            };

            module(function ($provide) {
                $provide.value("Pictures", picturesMock);
                $provide.value("Endpoints", endpointsMock);
                $provide.value("FormService", formServiceMock);
            });
        });

        beforeEach(inject(function (_PicturesService_) {
            PicturesService = _PicturesService_;
            spyOn(picturesMock, "get").andCallThrough();
            spyOn(formServiceMock, "send").andCallThrough();
        }));

        it("PicturesService should be not null", function () {
            expect(!!PicturesService).toBe(true);
        });
    });
});