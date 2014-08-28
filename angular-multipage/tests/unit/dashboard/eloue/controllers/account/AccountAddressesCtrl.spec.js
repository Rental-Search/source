define(["angular-mocks", "eloue/controllers/account/AccountAddressesCtrl"], function () {

    describe("Controller: AccountAddressesCtrl", function () {

        var AccountAddressesCtrl,
            scope,
            usersServiceMock,
            addressesServiceMock,
            utilsServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return {$promise: {then: function () {
                        return {result: {id: 1}}
                    }}}
                }
            };

            addressesServiceMock = {
                getAddressesByPatron: function (patronId) {
                    console.log("addressesServiceMock:getAddressesByPatron called with patronId = " + patronId);
                    return {$promise: {then: function () {
                        return {result: {id: 1}}
                    }}}
                }
            };

            utilsServiceMock = {getIdFromUrl: function (url) {
                return 1;
            }};

            module(function ($provide) {
                $provide.value("UsersService", usersServiceMock);
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(usersServiceMock, "getMe").andCallThrough();
            spyOn(addressesServiceMock, "getAddressesByPatron").andCallThrough();
            $rootScope.$digest();
            AccountAddressesCtrl = $controller('AccountAddressesCtrl', { $scope: scope, UsersService: usersServiceMock, AddressesService: addressesServiceMock, UtilsService: utilsServiceMock });
            expect(usersServiceMock.getMe).toHaveBeenCalled();
        }));

        it("AccountAddressesCtrl should be not null", function () {
            expect(!!AccountAddressesCtrl).toBe(true);
        });
    });
});