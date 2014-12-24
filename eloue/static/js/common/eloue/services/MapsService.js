"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values"], function (EloueCommon) {
    /**
     * Service for uploading forms.
     */
    EloueCommon.factory("MapsService", ["$document", function ($document) {
        var mapsService = {};

        mapsService.loadGoogleMaps = function () {
            var script = $document[0].createElement("script");
            script.type = "text/javascript";
            script.src = "https://maps.googleapis.com/maps/api/js?sensor=false&libraries=places&language=fr&callback=googleMapsLoaded";
            $document[0].body.appendChild(script);
        };

        mapsService.range = function (zoom) {
            if (zoom >= 14) {
                return 0.5;
            }
            if (zoom >= 13) {
                return 1;
            }
            if (zoom >= 12) {
                return 3;
            }
            if (zoom >= 11) {
                return 6;
            }
            if (zoom >= 10) {
                return 15;
            }
            if (zoom >= 9) {
                return 25;
            }
            if (zoom >= 8) {
                return 100;
            }
            if (zoom >= 7) {
                return 200;
            }
            if (zoom >= 6) {
                return 350;
            }
            if (zoom >= 5) {
                return 500;
            }
            if (zoom >= 4) {
                return 700;
            }
            return 1000;
        };

        mapsService.zoom = function (radius) {
            if (radius <= 0.5) {
                return 14;
            }
            if (radius <= 1) {
                return 13;
            }
            if (radius <= 3) {
                return 12;
            }
            if (radius <= 6) {
                return 11;
            }
            if (radius <= 15) {
                return 10;
            }
            if (radius <= 25) {
                return 9;
            }
            if (radius <= 100) {
                return 8;
            }
            if (radius <= 200) {
                return 7;
            }
            if (radius <= 350) {
                return 6;
            }
            if (radius <= 500) {
                return 5;
            }
            if (radius <= 700) {
                return 4;
            }
            return 3;
        };

        return mapsService;
    }]);
});
