define([
    'eloue/app'
], function (EloueWidgetsApp) {
    'use strict';
    /**
     * Controller to manage cookies ribbon on the top of the screen.
     */
    EloueWidgetsApp.controller('CookiesCtrl', [
        '$scope',
        '$rootScope',
        'ipCookie',
        function ($scope, $rootScope, ipCookie) {

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

            $rootScope.$on('loggedIn', function() {
                // When user logged in, remove the ribbon.
                $scope.acceptCookies(true);
            });

            $scope.showCookiesRibbon = ipCookie('cookiesAccepted') == false || ipCookie('cookiesAccepted') == undefined;
        }]);
});
