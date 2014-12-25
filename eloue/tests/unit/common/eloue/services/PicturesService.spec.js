define(["angular-mocks", "eloue/services/PicturesService"], function () {

    describe("Service: PicturesService", function () {

        var PicturesService,
            picturesMock,
            endpointsMock,
            formServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            picturesMock = {
                get: function () {
                },
                delete: function(id) {}
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
            spyOn(picturesMock, "get").and.callThrough();
            spyOn(picturesMock, "delete").and.callThrough();
            spyOn(formServiceMock, "send").and.callThrough();
        }));

        it("PicturesService should be not null", function () {
            expect(!!PicturesService).toBe(true);
        });

        it("PicturesService:savePicture", function () {
            PicturesService.savePicture({}, undefined, undefined);
            expect(formServiceMock.send).toHaveBeenCalled();
        });

        it("PicturesService:deletePicture", function () {
            var pictureId = 1;
            PicturesService.deletePicture(pictureId);
            expect(picturesMock.delete).toHaveBeenCalledWith({id: pictureId});
        });
    });
});