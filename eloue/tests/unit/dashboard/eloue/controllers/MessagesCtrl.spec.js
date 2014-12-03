define(["angular-mocks", "eloue/controllers/MessagesCtrl"], function () {

    describe("Controller: MessagesCtrl", function () {

        var MessagesCtrl,
            scope,
            usersServiceMock,
            utilsServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            scope.currentUserPromise = {
                then: function () {
                    return {response: {}}
                }
            };
            usersServiceMock = {};
            utilsServiceMock = {};

            MessagesCtrl = $controller('MessagesCtrl', { $scope: scope, UsersService: usersServiceMock,
                UtilsService: utilsServiceMock});
        }));

        it("MessagesCtrl should be not null", function () {
            expect(!!MessagesCtrl).toBe(true);
        });
    });
});