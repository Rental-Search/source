define(["angular-mocks", "eloue/controllers/items/ItemsShippingCtrl"], function () {

    describe("Controller: ItemsShippingCtrl", function () {

        var ItemsShippingCtrl,
            scope,
            stateParams;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.markListItemAsSelected = function(prefix, id) {};
            scope.initCustomScrollbars = function() {};
            stateParams = {
                id: 1
            };

            ItemsShippingCtrl = $controller('ItemsShippingCtrl', { $scope: scope, $stateParams: stateParams });
        }));

        it("ItemsShippingCtrl should be not null", function () {
            expect(!!ItemsShippingCtrl).toBe(true);
        });
    });
});
