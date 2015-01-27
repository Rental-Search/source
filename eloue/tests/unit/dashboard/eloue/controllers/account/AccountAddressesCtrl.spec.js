define(["angular-mocks", "eloue/controllers/account/AccountAddressesCtrl"], function () {

    describe("Controller: AccountAddressesCtrl", function () {

        var AccountAddressesCtrl,
            scope,
            usersServiceMock,
            addressesServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return simpleServiceResponse;
                }
            };

            addressesServiceMock = {
                getAddressesByPatron: function (patronId) {
                    console.log("addressesServiceMock:getAddressesByPatron called with patronId = " + patronId);
                    return simpleServiceResponse;
                }
            };


            module(function ($provide) {
                $provide.value("UsersService", usersServiceMock);
                $provide.value("AddressesService", addressesServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.markListItemAsSelected = function(prefix, id) {};
            spyOn(usersServiceMock, "getMe").and.callThrough();
            spyOn(addressesServiceMock, "getAddressesByPatron").and.callThrough();
            $rootScope.$digest();
            AccountAddressesCtrl = $controller('AccountAddressesCtrl', { $scope: scope, UsersService: usersServiceMock, AddressesService: addressesServiceMock });
            expect(usersServiceMock.getMe).toHaveBeenCalled();
        }));

        it("AccountAddressesCtrl should be not null", function () {
            expect(!!AccountAddressesCtrl).toBe(true);
        });
    });
});