"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values"], function (EloueCommon) {
    /**
     * Service for managing comments.
     */
    EloueCommon.factory("CommentsService", [
        "Comments",
        "Endpoints",
        function (Comments, Endpoints) {
            var commentsService = {};

            commentsService.getCommentList = function (bookingUUID) {
                return Comments.get({_cache: new Date().getTime(), booking: bookingUUID}).$promise;
            };

            commentsService.postComment = function (bookingUUID, comment, rate) {
                var bookingUrl = Endpoints.api_url + "bookings/" + bookingUUID + "/";
                return Comments.save({
                    booking: bookingUrl,
                    comment: comment,
                    rate: rate
                });
            };

            return commentsService;
        }
    ]);
});
