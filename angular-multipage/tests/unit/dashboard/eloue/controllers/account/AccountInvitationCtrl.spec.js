define(["angular-mocks", "eloue/controllers/account/AccountInvitationCtrl"], function() {

    describe("Controller: AccountInvitationCtrl", function () {

        var AccountInvitationCtrl,
            scope;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            AccountInvitationCtrl = $controller('AccountInvitationCtrl', { $scope: scope });
        }));

        it("AccountInvitationCtrl should be not null", function () {
            expect(!!AccountInvitationCtrl).toBe(true);
        });
    });
});