define(["angular-mocks", "eloue/controllers/account/AccountProfileCtrl"], function() {

    describe("Controller: AccountProfileCtrl", function () {

        var AccountProfileCtrl,
            scope,
            usersServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            usersServiceMock = {
                sendForm: function (userId, form, successCallback, errorCallback) {
                    console.log("usersServiceMock:sendForm called with userId = " + userId);
                }
            };

            module(function($provide) {
                $provide.value("UsersService", usersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.currentUserPromise = {
                then: function() {}
            };
            scope.currentUser = { id: 1};
            spyOn(usersServiceMock, "sendForm").andCallThrough();

            AccountProfileCtrl = $controller('AccountProfileCtrl', { $scope: scope, UsersService: usersServiceMock });
        }));

        it("AccountProfileCtrl should be not null", function () {
            expect(!!AccountProfileCtrl).toBe(true);
        });

        it("AccountProfileCtrl:onFileChanged", function () {
            scope.onFileChanged();
            expect(usersServiceMock.sendForm).toHaveBeenCalled();
        });

        it("AccountProfileCtrl:dataFormSubmit", function () {
            scope.dataFormSubmit();
            expect(usersServiceMock.sendForm).toHaveBeenCalled();
        });
    });
});