define(["angular-mocks", "eloue/modules/booking/services/UserService"], function() {

    describe("Service: UserService", function () {

        var UserService, scope,
            usersResourceMock;

        beforeEach(module('EloueApp'));
        beforeEach(module('EloueApp.BookingModule'));

        beforeEach(function () {
            usersResourceMock = {get: function () {
                console.log("User resource mock called");
            }};

            module(function($provide) {
                $provide.value("Users", usersResourceMock);
            })
        });

        //TODO

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();

            spyOn(usersResourceMock, "get").andCallThrough();

            UserService = $controller('UserService', { $scope:scope, Users: usersResourceMock});
        }));

        it('should make a call to Users service', function () {
            scope.register();
            expect(usersResourceMock.get).toHaveBeenCalled();
        });
    });
});
