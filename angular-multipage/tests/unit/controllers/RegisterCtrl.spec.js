define(["angular-mocks", "eloue/modules/user_management/controllers/RegisterCtrl"], function() {

    describe("Controller: RegisterCtrl", function () {

        var RegisterCtrl,
            scope,
            usersServiceMock;

        beforeEach(module('EloueApp'));

        beforeEach(function () {
            usersServiceMock = {register: function () {
                console.log("User service mock called");
            }};

            module(function($provide) {
                $provide.value("Users", usersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(usersServiceMock, "register").andCallThrough();

            RegisterCtrl = $controller('RegisterCtrl', { $scope:scope, Users: usersServiceMock});
        }));

        it('should make a call to Users service', function () {
            scope.register();
            expect(usersServiceMock.register).toHaveBeenCalled();
        });
    });
});