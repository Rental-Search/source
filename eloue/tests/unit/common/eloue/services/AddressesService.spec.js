define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: AddressesService", function () {

        var AddressesService,
            q,
            addressesMock,
            endpointsMock,
            formServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            endpointsMock = {};
            addressesMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
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

        beforeEach(inject(function (_AddressesService_, $q) {
            AddressesService = _AddressesService_;
            q = $q;
            spyOn(addressesMock, "get").and.callThrough();
            spyOn(addressesMock, "update").and.callThrough();
            spyOn(addressesMock, "delete").and.callThrough();
            spyOn(formServiceMock, "send").and.callThrough();
        }));

        it("AddressesService should be not null", function () {
            expect(!!AddressesService).toBe(true);
        });

        it("AddressesService:getAddress", function () {
            var addressId = 1;
            AddressesService.getAddress(addressId);
            expect(addressesMock.get).toHaveBeenCalledWith({id: addressId, _cache: jasmine.any(Number)});
        });

        it("AddressesService:getAddressesByPatron", function () {
            var patronId = 1;
            AddressesService.getAddressesByPatron(patronId);
            expect(addressesMock.get).toHaveBeenCalledWith({patron: patronId, _cache: jasmine.any(Number)});
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