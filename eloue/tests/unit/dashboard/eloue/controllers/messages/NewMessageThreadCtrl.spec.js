define(["angular-mocks", "eloue/controllers/messages/NewMessageThreadCtrl"], function() {

    describe("Controller: NewMessageThreadCtrl", function () {

        var NewMessageThreadCtrl,
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
            scope.currentUserPromise = {
                then: function () {
                }
            };

            spyOn(usersServiceMock, "getMe").andCallThrough();

            NewMessageThreadCtrl = $controller('NewMessageThreadCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("NewMessageThreadCtrl should be not null", function () {
            expect(!!NewMessageThreadCtrl).toBe(true);
        });
    });
});