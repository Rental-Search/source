define(["angular-mocks", "eloue/controllers/messages/MessageDetailCtrl"], function() {

    describe("Controller: MessageDetailCtrl", function () {

        var MessageDetailCtrl,
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

            MessageDetailCtrl = $controller('MessageDetailCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("MessageDetailCtrl should be not null", function () {
            expect(!!MessageDetailCtrl).toBe(true);
        });
    });
});