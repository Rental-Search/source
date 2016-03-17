define([
    "eloue/app"
], function (EloueWidgetsApp) {
    "use strict";
    /**
     * Controller to run scripts necessary for home page.
     */
    EloueWidgetsApp.controller("HomePageCtrl", [
        "$scope",
        "$document",
        "$window",
        "MapsService",
        function ($scope, $document, $window, MapsService) {

            /**
             * Activate geolocation search.
             */
            $window.googleMapsLoaded = function () {
                $("#geolocate").formmapper({
                    details: "form",
                    componentRestrictions: {country: 'fr'}
                });
            };

            /**
             * Insert YouTube video into defined container, add play on modal open and stop on modal hide
             */
            $scope.addVideoPlayer = function () {
                var tag = $document[0].createElement("script"),
                    firstScriptTag = $document[0].getElementsByTagName("script")[0],
                    videoModal = $("#videoModal"),
                    videoId = $("#videoId"),
                    player;


                tag.src = "https://www.youtube.com/iframe_api";
                firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
                videoModal.on("shown.bs.modal", function () {
                    player = new YT.Player("videoContainer", {
                        height: "480",
                        width: "640",
                        videoId: videoId.val(),
                        events: {
                            "onReady": $scope.onPlayerReady
                        }
                    });
                });
                videoModal.on("hidden.bs.modal", function () {
                    player.destroy();
                });
            };

            /**
             * Player loaded callback.
             * @param event player ready event
             */
            $scope.onPlayerReady = function (event) {
                event.target.playVideo();
            };

            //Load video player on home page loaded
            $scope.addVideoPlayer();

            MapsService.loadGoogleMaps();
        }]);
});
