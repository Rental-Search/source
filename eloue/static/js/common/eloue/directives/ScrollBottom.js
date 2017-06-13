define(['../../../common/eloue/commonApp'], function (EloueCommon) {
    'use strict';
    /**
     * Directive to watch specified collection and scroll its container to the bottom when collection changed.
     */
    EloueCommon.directive('scrollBottom', ['$timeout', function ($timeout) {
        return {
            scope: {
                scrollBottom: '='
            },
            link: function (scope, element) {
                scope.$watchCollection('scrollBottom', function(newValue) {
                    if (newValue) {
                        $timeout(function () {
                            var el = $(element);
                            el.scrollTop(el[0].scrollHeight)
                        });
                    }
                })
            }
        };
    }]);
});
