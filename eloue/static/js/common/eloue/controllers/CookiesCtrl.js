define([
    'eloue/app'
], function (EloueWidgetsApp) {
    'use strict';
    /**
     * Controller to manage cookies ribbon on the top of the screen.
     */
    EloueWidgetsApp.controller('CookiesCtrl', [
        '$scope',
        'ipCookie',
        function ($scope, ipCookie) {

            /**
             * Update cookie value to 'true'.
             * @param removeRibbon additional param to remove ribbon or not.
             */
            $scope.acceptCookies = function (removeRibbon) {
                ipCookie('cookiesAccepted', 'true', {path: '/', expires: 1000});
                if (removeRibbon) {
                    $scope.showCookiesRibbon = false;
                }
            };

            $scope.showCookiesRibbon = ipCookie('cookiesAccepted') == false || ipCookie('cookiesAccepted') == undefined;
        }]);
});
