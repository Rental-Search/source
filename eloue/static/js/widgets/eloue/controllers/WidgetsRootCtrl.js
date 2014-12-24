define([
    "eloue/app",
    "../../../common/eloue/services/MapsService"
], function (EloueWidgetsApp) {
    "use strict";
    EloueWidgetsApp.controller("WidgetsRootCtrl", [
        "$scope",
        "$window",
        "$document",
        "MapsService",
        function ($scope, $window, $document, MapsService) {
            (function (d, s, id) {
                var js, fjs = d.getElementsByTagName(s)[0];
                if (d.getElementById(id)) return;
                js = d.createElement(s);
                js.id = id;
                js.src = "//connect.facebook.net/fr_FR/sdk.js#xfbml=1&version=v2.0&appId=197983240245844";
                fjs.parentNode.insertBefore(js, fjs);
            }($document[0], "script", "facebook-jssdk"));
        }
    ]);
});
