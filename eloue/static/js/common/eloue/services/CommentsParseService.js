"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for parsing comments.
     */
    EloueCommon.factory("CommentsParseService", [function () {
        var commentsParseService = {};

        commentsParseService.parseComment = function (commentData, authorData) {
            var commentResult = angular.copy(commentData);

            // Parse author
            if (!!authorData) {
                commentResult.author = authorData;
            }

            return commentResult;
        };

        return commentsParseService;
    }]);
});
