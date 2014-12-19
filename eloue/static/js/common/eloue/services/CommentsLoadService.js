"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values",
    "../../../common/eloue/services/UsersService",
    "../../../common/eloue/services/UtilsService",
    "../../../common/eloue/services/CommentsParseService"], function (EloueCommon) {
    /**
     * Service for managing comments.
     */
    EloueCommon.factory("CommentsLoadService", [
        "$q",
        "Comments",
        "Endpoints",
        "UsersService",
        "UtilsService",
        "CommentsParseService",
        function ($q, Comments, Endpoints, UsersService, UtilsService, CommentsParseService) {
            var commentsLoadService = {};

            commentsLoadService.getCommentList = function (bookingUUID) {
                var deferred = $q.defer();
                var commentListPromises = [];

                // Load comments
                Comments.get({
                    booking: bookingUUID,
                    _cache: new Date().getTime()
                }).$promise.then(function (commentListData) {
                        angular.forEach(commentListData.results, function (commentData, key) {
                            var commentDeferred = $q.defer();

                            // Get author id
                            var authorId = UtilsService.getIdFromUrl(commentData.author);
                            // Load author
                            UsersService.get(authorId).$promise.then(function (authorData) {
                                var comment = CommentsParseService.parseComment(commentData, authorData);
                                commentDeferred.resolve(comment);
                            });

                            commentListPromises.push(commentDeferred.promise);
                        });

                        $q.all(commentListPromises).then(function (results) {
                            deferred.resolve(results);
                        });
                    });

                return deferred.promise;
            };

            commentsLoadService.postComment = function (bookingUUID, comment, rate) {
                var bookingUrl = Endpoints.api_url + "bookings/" + bookingUUID + "/";
                return Comments.save({
                    booking: bookingUrl,
                    comment: comment,
                    rate: rate
                });
            };

            return commentsLoadService;
        }
    ]);
});
