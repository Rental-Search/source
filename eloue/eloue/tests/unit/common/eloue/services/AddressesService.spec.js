define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: AddressesService", function () {

        var AddressesService,
            addressesMock,
            endpointsMock,
            formServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            endpointsMock = {};
            addressesMock = {
                get: function () {

                },
                update: function () {

                },
                delete: function () {

                }
            };
            formServiceMock = {
                send: function (method, url, $form, successCallback, errorCallback) {

                }
            };

            module(function ($provide) {
                $provide.value("Addresses", addressesMock);
                $provide.value("FormService", formServiceMock);
            });
        });

        beforeEach(inject(function (_AddressesService_) {
            AddressesService = _AddressesService_;
            spyOn(addressesMock, "get").andCallThrough();
            spyOn(addressesMock, "update").andCallThrough();
            spyOn(addressesMock, "delete").andCallThrough();
            spyOn(formServiceMock, "send").andCallThrough();
        }));

        it("AddressesService should be not null", function () {
            expect(!!AddressesService).toBe(true);
        });

        it("AddressesService:deleteAddress", function () {
            var addressId = 1;
            AddressesService.deleteAddress(addressId);
            expect(addressesMock.delete).toHaveBeenCalledWith({id: addressId});
        });

        it("AddressesService:update", function () {
            var address = {
                id: 1
            };
            AddressesService.update(address);
            expect(addressesMock.update).toHaveBeenCalledWith({id: address.id}, address);
        });
    });
});