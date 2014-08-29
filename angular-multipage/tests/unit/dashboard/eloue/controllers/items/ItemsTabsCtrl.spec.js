define(["angular-mocks", "eloue/controllers/items/ItemsTabsCtrl"], function() {

    describe("Controller: ItemsTabsCtrl", function () {

        var ItemsTabsCtrl,
            scope,
            stateParams;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            stateParams = {
                id: 1
            };

            ItemsTabsCtrl = $controller('ItemsTabsCtrl', { $scope: scope, $stateParams: stateParams });
            expect(scope.selectedItemId).toEqual(stateParams.id);
        }));

        it("ItemsTabsCtrl should be not null", function () {
            expect(!!ItemsTabsCtrl).toBe(true);
        });
    });
});