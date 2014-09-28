define(["angular-mocks", "eloue/controllers/MessagesCtrl"], function () {

    describe("Controller: MessagesCtrl", function () {

        var MessagesCtrl,
            scope,
            rootScope;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            scope.currentUserPromise = {
                then: function () {
                    return {response: {}}
                }
            };

            MessagesCtrl = $controller('MessagesCtrl', { $scope: scope, $rootScope: rootScope});
        }));

        it("MessagesCtrl should be not null", function () {
            expect(!!MessagesCtrl).toBe(true);
        });
    });
});