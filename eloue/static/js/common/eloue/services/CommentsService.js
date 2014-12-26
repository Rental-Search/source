define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values",
    "../../../common/eloue/services/UsersService",
    "../../../common/eloue/services/UtilsService"], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing comments.
     */
    EloueCommon.factory("CommentsService", [
        "$q",
        "Comments",
        "Endpoints",
        "UsersService",
        "UtilsService",
        function ($q, Comments, Endpoints, UsersService, UtilsService) {
            var commentsService = {};

            commentsService.postComment = function (bookingUUID, comment, rate) {
                var bookingUrl = Endpoints.api_url + "bookings/" + bookingUUID + "/";
                return Comments.save({
                    booking: bookingUrl,
                    comment: comment,
                    rate: rate
                }).$promise;
            };

            commentsService.getCommentList = function (bookingUUID) {
                var deferred = $q.defer();
                var commentListPromises = [];

                // Load comments
                Comments.get({
                    booking: bookingUUID,
                    _cache: new Date().getTime()
                }).$promise.then(
                    function (commentListData) {
                        angular.forEach(commentListData.results, function (commentData, key) {
                            var commentDeferred = $q.defer(),
                                authorId = UtilsService.getIdFromUrl(commentData.author);
                            // Load author
                            UsersService.get(authorId).$promise.then(function (authorData) {
                                var comment = commentsService.parseComment(commentData, authorData);
                                commentDeferred.resolve(comment);
                            });

                            commentListPromises.push(commentDeferred.promise);
                        });

                        $q.all(commentListPromises).then(function (results) {
                            deferred.resolve(results);
                        });
                    }
                );
                return deferred.promise;
            };

            commentsService.parseComment = function (commentData, authorData) {
                var commentResult = angular.copy(commentData);
                // Parse author
                if (authorData) {
                    commentResult.author = authorData;
                }
                return commentResult;
            };

            return commentsService;
        }
    ]);
});
