define(["angular-mocks", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function() {

    describe("Controller: ProductDetailsCtrl", function () {

        var ProductDetailsCtrl,
            scope,
            callServiceMock,
            productServiceMock;

        beforeEach(module('EloueApp'));
        beforeEach(module('EloueApp.BookingModule'));

        beforeEach(function () {
            callServiceMock = {login: function () {
                console.log("Auth service mock called");
            }};

            module(function($provide) {
                $provide.value("AuthService", authServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(authServiceMock, "login").andCallThrough();

            ProductDetailsCtrl = $controller('ProductDetailsCtrl', { $scope:scope, AuthService: authServiceMock});
        }));

        it('should make a call to authService', function () {
            scope.login();
            expect(authServiceMock.login).toHaveBeenCalled();
        });
    });
});