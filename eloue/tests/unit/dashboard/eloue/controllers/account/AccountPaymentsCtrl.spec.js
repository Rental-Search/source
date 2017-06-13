define(["angular-mocks", "eloue/controllers/account/AccountPaymentsCtrl"], function() {

    describe("Controller: AccountPaymentsCtrl", function () {

        var AccountPaymentsCtrl,
            scope;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.markListItemAsSelected = function(prefix, id) {};
            AccountPaymentsCtrl = $controller('AccountPaymentsCtrl', { $scope: scope });
        }));

        it("AccountPaymentsCtrl should be not null", function () {
            expect(!!AccountPaymentsCtrl).toBe(true);
        });
    });
});