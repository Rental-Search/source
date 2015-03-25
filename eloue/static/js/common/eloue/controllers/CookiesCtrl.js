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
        '$location',
        'ipCookie',
        function ($scope, $rootScope, $location, ipCookie) {

            $rootScope.$on('loggedIn', function() {
                // When user logged in, check if cookie to display ribbon is set or not.
                $scope.showCookiesRibbon = ipCookie('cookiesAccepted') == false || ipCookie('cookiesAccepted') == undefined;

                // If user is on the "Terms" page, let's say, that user read cookies term, and there is no need to
                // display ribbon anymore. Update cookie, but keep the ribbon while he is on this page.
                if ($location.$$absUrl.indexOf('/conditions-generales/') != -1) {
                    $scope.acceptCookies(false);
                }
            });

            /**
             * Update cookie value to 'true'.
             * @param removeRibbon additional param to remove ribbon or not.
             */
            $scope.acceptCookies = function(removeRibbon) {
                ipCookie('cookiesAccepted', 'true', {path: '/', expires: 1000});
                if (removeRibbon) {
                    $scope.showCookiesRibbon = false;
                }
            };
        }]);
});
