define(["angular-mocks", "eloue/controllers/account/AccountPhonesCtrl"], function() {

    describe("Controller: AccountPhonesCtrl", function () {

        var AccountPhonesCtrl,
            scope;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.markListItemAsSelected = function(prefix, id) {};
            AccountPhonesCtrl = $controller('AccountPhonesCtrl', { $scope: scope});
        }));

        it("AccountPhonesCtrl should be not null", function () {
            expect(!!AccountPhonesCtrl).toBe(true);
        });
    });
});