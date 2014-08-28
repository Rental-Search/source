define(["angular-mocks", "eloue/controllers/BookingsCtrl"], function () {

    describe("Controller: BookingsCtrl", function () {

        var BookingsCtrl,
            scope,
            endpointsMock,
            bookingsLoadServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            endpointsMock = {
                api_url: "http://10.0.5.47:8200/api/2.0/"
            };
            bookingsLoadServiceMock = {
                getBookingList: function (page, author) {
                    console.log("bookingsLoadServiceMock:getBookingList called with page = " + page + ", author = " + author);
                    return {then: function () {
                        return {response: {}}
                    }}
                }
            };

            module(function ($provide) {
                $provide.value("Endpoints", endpointsMock);
                $provide.value("BookingsLoadService", bookingsLoadServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.currentUserPromise = {
                then: function () {
                }
            };
            scope.currentUser = { id: 1};
            scope.currentUserUrl = Endpoints.api_url + "users/" + scope.currentUser.id + "/";
            spyOn(bookingsLoadServiceMock, "getBookingList").andCallThrough();

            BookingsCtrl = $controller('BookingsCtrl', { $scope: scope, Endpoints: endpointsMock, BookingsLoadService: bookingsLoadServiceMock });
        }));

        it("BookingsCtrl should be not null", function () {
            expect(!!BookingsCtrl).toBe(true);
        });

        it("BookingsCtrl:filterByOwner", function () {
            scope.filterByOwner();
            expect(scope.bookingFilter.owner).toEqual(scope.currentUserUrl);
            expect(scope.bookingFilter.borrower).toBeUndefined();
        });

        it("BookingsCtrl:filterByBorrower", function () {
            scope.filterByBorrower();
        });

        it("BookingsCtrl:filterByBoth", function () {
            scope.filterByBoth();
        });

        it("BookingsCtrl:filterByState", function () {
            scope.filterByState();
        });
    });
});