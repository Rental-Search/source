define(["angular-mocks", "eloue/controllers/account/AccountAddressesCtrl"], function() {

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
                    return { id: 1190};
                }
            };

            module(function($provide) {
                $provide.value("UsersService", usersServiceMock);
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(usersServiceMock, "getMe").andCallThrough();

            AccountAddressesCtrl = $controller('AccountAddressesCtrl', { $scope: scope, UsersService: usersServiceMock, AddressesService: addressesServiceMock, UtilsService: utilsServiceMock });
        }));

        it("AccountAddressesCtrl should be not null", function () {
            expect(!!AccountAddressesCtrl).toBe(true);
        });
    });
});