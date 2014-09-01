define(["angular-mocks", "eloue/controllers/account/AccountVerificationCtrl"], function() {

    describe("Controller: AccountVerificationCtrl", function () {

        var AccountVerificationCtrl, scope;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            AccountVerificationCtrl = $controller('AccountVerificationCtrl', { $scope: scope});
        }));

        it("AccountVerificationCtrl should be not null", function () {
            expect(!!AccountVerificationCtrl).toBe(true);
        });
    });
});