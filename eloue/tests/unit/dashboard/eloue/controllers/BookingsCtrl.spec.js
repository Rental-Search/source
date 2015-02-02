define(["angular-mocks", "eloue/controllers/BookingsCtrl"], function () {

    describe("Controller: BookingsCtrl", function () {

        var BookingsCtrl,
            scope,
            timeout,
            usersServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            usersServiceMock = {
                getMe: function () {
                    console.log("usersServiceMock:getMe called");
                    return simpleServiceResponse;
                }
            };

            module(function ($provide) {
                $provide.value("UsersService", usersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $timeout, $controller) {
            scope = $rootScope.$new();
            timeout = $timeout;
            scope.currentUserPromise = {
                then: function () {
                }
            };
            scope.markListItemAsSelected = function(prefix, id) {};
            scope.currentUser = { id: 1};
            spyOn(usersServiceMock, "getMe").and.callThrough();
            spyOn(scope, "$broadcast").and.callThrough();

            BookingsCtrl = $controller('BookingsCtrl', { $scope: scope, $timeout: timeout, UsersService: usersServiceMock });
        }));

        it("BookingsCtrl should be not null", function () {
            expect(!!BookingsCtrl).toBe(true);
        });

        it("BookingsCtrl:filterByOwner", function () {
            scope.filterByOwner();
            expect(scope.bookingFilter.owner).toEqual(scope.currentUser.id);
            expect(scope.bookingFilter.borrower).toBeUndefined();
        });

        it("BookingsCtrl:filterByBorrower", function () {
            scope.filterByBorrower();
            expect(scope.bookingFilter.borrower).toEqual(scope.currentUser.id);
            expect(scope.bookingFilter.owner).toBeUndefined();
        });

        it("BookingsCtrl:filterByBoth", function () {
            scope.filterByBoth();
            expect(scope.bookingFilter.borrower).toBeUndefined();
            expect(scope.bookingFilter.owner).toBeUndefined();
        });

        it("BookingsCtrl:filterByState", function () {
            scope.filterByState();
            expect(scope.bookingFilter.state).toEqual(scope.stateFilter);
        });

        it("BookingsCtrl:filter", function () {
            scope.filter();
            expect(scope.$broadcast).toHaveBeenCalledWith("startLoading",
                {
                    parameters: [scope.currentUser.id, scope.stateFilter, scope.bookingFilter.borrower, scope.bookingFilter.owner],
                    shouldReloadList: true
                });
        });
    });
});