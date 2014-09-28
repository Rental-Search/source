define(["angular-mocks", "eloue/controllers/bookings/BookingDetailCtrl"], function () {

    describe("Controller: BookingDetailCtrl", function () {

        var BookingDetailCtrl,
            scope,
            stateParams,
            bookingsLoadServiceMock,
            commentsLoadServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            bookingsLoadServiceMock = {
                getBookingDetails: function (bookingUUID) {
                    console.log("bookingsLoadServiceMock:getBookingDetails called with bookingUUID = " + bookingUUID);
                    return {then: function () {
                        return {response: {}}
                    }}
                }
            };
            commentsLoadServiceMock = {
                getCommentList: function (bookingUUID) {
                    console.log("commentsLoadServiceMock:getCommentList called with bookingUUID = " + bookingUUID);
                    return {then: function () {
                        return {response: {}}
                    }}
                },
                postComment: function (bookingUUID, comment, rate) {
                    console.log("commentsLoadServiceMock:postComment called with bookingUUID = " + bookingUUID + ", comment = " + comment + ", rate = " + rate);
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };

            module(function ($provide) {
                $provide.value("BookingsLoadService", bookingsLoadServiceMock);
                $provide.value("CommentsLoadService", commentsLoadServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            stateParams = {};
            spyOn(bookingsLoadServiceMock, "getBookingDetails").andCallThrough();
            spyOn(commentsLoadServiceMock, "getCommentList").andCallThrough();
            spyOn(commentsLoadServiceMock, "postComment").andCallThrough();

            BookingDetailCtrl = $controller('BookingDetailCtrl', { $scope: scope, $stateParams: stateParams, BookingsLoadService: bookingsLoadServiceMock, CommentsLoadService: commentsLoadServiceMock });
            expect(bookingsLoadServiceMock.getBookingDetails).toHaveBeenCalled();
            expect(commentsLoadServiceMock.getCommentList).toHaveBeenCalled();
        }));

        it("BookingDetailCtrl should be not null", function () {
            expect(!!BookingDetailCtrl).toBe(true);
        });

        it("BookingDetailCtrl:postComment", function () {
            stateParams.uuid = 1;
            scope.comment = {
                text: 'text',
                rate: 1
            };
            scope.postComment();
            expect(commentsLoadServiceMock.postComment).toHaveBeenCalledWith(stateParams.uuid, scope.comment.text, scope.comment.rate);
        });
    });
});