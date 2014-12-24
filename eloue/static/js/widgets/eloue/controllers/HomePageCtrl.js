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
        function ($scope, $document) {

            /**
             * Insert YouTube video into defined container, add play on modal open and stop on modal hide
             */
            $scope.addVideoPlayer = function () {
                var tag = $document[0].createElement("script");

                tag.src = "https://www.youtube.com/iframe_api";
                var firstScriptTag = $document[0].getElementsByTagName("script")[0];
                firstScriptTag.parentNode.insertBefore(tag, firstScriptTag);
                var videoModal = $("#videoModal");
                var player;

                videoModal.on("shown.bs.modal", function () {
                    player = new YT.Player("videoContainer", {
                        height: "480",
                        width: "640",
                        videoId: "nERu_2pSSb0",
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
        }]);
});
