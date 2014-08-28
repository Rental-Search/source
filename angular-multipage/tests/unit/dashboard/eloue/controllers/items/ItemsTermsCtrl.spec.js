define(["angular-mocks", "eloue/controllers/items/ItemsTermsCtrl"], function() {

    describe("Controller: ItemsTermsCtrl", function () {

        var ItemsTermsCtrl,
            scope,
            usersServiceMock;

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
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(usersServiceMock, "getMe").andCallThrough();

            ItemsTermsCtrl = $controller('ItemsTermsCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("ItemsTermsCtrl should be not null", function () {
            expect(!!ItemsTermsCtrl).toBe(true);
        });
    });
});