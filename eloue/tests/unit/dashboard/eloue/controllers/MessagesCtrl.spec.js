define(["angular-mocks", "eloue/controllers/MessagesCtrl"], function () {

    describe("Controller: MessagesCtrl", function () {

        var MessagesCtrl,
            scope,
            usersServiceMock,
            utilsServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            usersServiceMock = {
                getMe: function (successCallback, errorCallback) {
                    console.log("usersServiceMock:getMe");
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {}
            };

            module(function ($provide) {
                $provide.value("UsersService", usersServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            scope.currentUserPromise = {
                then: function () {
                    return {response: {}}
                }
            };

            spyOn(utilsServiceMock, "getIdFromUrl").and.callThrough();
            spyOn(usersServiceMock, "getMe").and.callThrough();

            MessagesCtrl = $controller('MessagesCtrl', { $scope: scope, UsersService: usersServiceMock,
                UtilsService: utilsServiceMock});
        }));

        it("MessagesCtrl should be not null", function () {
            expect(!!MessagesCtrl).toBe(true);
        });

        it("MessagesCtrl:shouldMarkAsUnread", function () {
            scope.currentUser = {
                id: 1
            };
            var lastMessage= {};
            scope.shouldMarkAsUnread(lastMessage);
        });
    });
});