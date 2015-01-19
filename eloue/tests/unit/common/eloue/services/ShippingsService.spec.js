define(["angular-mocks", "eloue/services/ShippingsService"], function () {

    describe("Service: ShippingsService", function () {

        var ShippingsService,
            shippingsMock,
            endpointsMock,
            utilsServiceMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            shippingsMock = {
                get: function () {
                    return simpleResourceResponse;
                },
                save: function() {
                    return simpleResourceResponse;
                }
            };
            endpointsMock = {
                api_url: "/api/2.0/"
            };
            utilsServiceMock = {
                downloadPdfFile: function (url, filename) {}
            };
            module(function ($provide) {
                $provide.value("Shippings", shippingsMock);
                $provide.value("Endpoints", endpointsMock);
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_ShippingsService_) {
            ShippingsService = _ShippingsService_;
            spyOn(shippingsMock, "get").and.callThrough();
            spyOn(shippingsMock, "save").and.callThrough();
            spyOn(utilsServiceMock, "downloadPdfFile").and.callThrough();
        }));

        it("ShippingsService should be not null", function () {
            expect(!!ShippingsService).toBe(true);
        });

        it("ShippingsService:getByBooking", function () {
            var bookingUUID = 1;
            ShippingsService.getByBooking(bookingUUID);
            expect(shippingsMock.get).toHaveBeenCalledWith({_cache: jasmine.any(Number), booking: bookingUUID});
        });

        it("ShippingsService:saveShipping", function () {
            var shipping = {};
            ShippingsService.saveShipping(shipping);
            expect(shippingsMock.save).toHaveBeenCalledWith(shipping);
        });

        it("ShippingsService:downloadVoucher", function () {
            var id = 1, isOwner = true;
            ShippingsService.downloadVoucher(id, isOwner);
            expect(utilsServiceMock.downloadPdfFile).toHaveBeenCalledWith(endpointsMock.api_url + "shippings/" + id + "/document/?back=true", "voucher.pdf");
        });
    });
});
