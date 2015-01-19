define(["angular-mocks", "eloue/controllers/MessagesCtrl"], function () {

    describe("Controller: MessagesCtrl", function () {

        var MessagesCtrl,
            scope,
            usersServiceMock,
            utilsServiceMock,
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
            utilsServiceMock = {
                getIdFromUrl: function (url) {
                    return url;
                }
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

        it("MessagesCtrl:shouldMarkAsUnread:true", function () {
            scope.currentUser = {
                id: 1
            };
            var lastMessage= {
                read_at: null,
                recipient: scope.currentUser.id
            };
            var result = scope.shouldMarkAsUnread(lastMessage);
            expect(result).toBeTruthy();
        });

        it("MessagesCtrl:shouldMarkAsUnread:false", function () {
            scope.currentUser = {
                id: 1
            };
            var lastMessage= {
                read_at: "2014-11-30 12:00:00",
                recipient: scope.currentUser.id
            };
            var result = scope.shouldMarkAsUnread(lastMessage);
            expect(result).toBeFalsy();
        });
    });
});