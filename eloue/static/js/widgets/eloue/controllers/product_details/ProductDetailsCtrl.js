define([
    "eloue/app",
    "../../../../common/eloue/services/MapsService"
], function (EloueWidgetsApp) {
    "use strict";

    EloueWidgetsApp.controller("ProductDetailsCtrl", [
        "$scope", "$window", "$document", "MapsService",
        function ($scope, MapsService) {

            $window.googleMapsLoaded = function () {
                $("#geolocate").formmapper({
                    details: "form"
                });

                var canvasId = "map-canvas-small", mapCanvasSmall = $document[0].getElementById(canvasId);
                if (mapCanvasSmall) {
                    var mapContainer = $("#" + canvasId);
                    var product = {
                        lat: mapContainer.attr("locationX"),
                        lng: mapContainer.attr("locationY")
                    };

                    var productMapOptions = {
                        zoom: 16,
                        disableDefaultUI: true,
                        zoomControl: true,
                        center: new google.maps.LatLng(product.lat, product.lng),
                        mapTypeId: google.maps.MapTypeId.ROADMAP
                    };
                    var productMap = new google.maps.Map(mapCanvasSmall, productMapOptions);
                    var circleOptions = {
                        strokeColor: "#3c763d",
                        strokeOpacity: 0.8,
                        strokeWeight: 2,
                        fillColor: "#3c763d",
                        fillOpacity: 0.35,
                        map: productMap,
                        center: new google.maps.LatLng(product.lat, product.lng),
                        radius: 100
                    };
                    var locationCircle = new google.maps.Circle(circleOptions);
                }
            };

            $scope.activateProductImageAnimation = function () {
                var slideImgs = [].slice.call($(".carousel-wrapper").find("img"));
                for (var index = 0; index < slideImgs.length; index++) {
                    var proportions = $(slideImgs[index]).width() / $(slideImgs[index]).height(),
                        parent = $(slideImgs[index]).parent(),
                        parentProportions = $(parent).width() / $(parent).height();

                    if (proportions < parentProportions) {
                        $(slideImgs[index]).addClass("expand-v");
                    } else {
                        $(slideImgs[index]).addClass("expand-h");
                    }
                }
            };

            $scope.activateSocialButtons = function() {
                $window.___gcfg = {lang: "fr"};
                (function () {
                    var po = $document[0].createElement("script");
                    po.type = "text/javascript";
                    po.async = true;
                    po.src = "https://apis.google.com/js/platform.js";
                    var s = $document[0].getElementsByTagName("script")[0];
                    s.parentNode.insertBefore(po, s);
                })();

                !function (d, s, id) {
                    var js, fjs = d.getElementsByTagName(s)[0], p = /^http:/.test(d.location) ? "http" : "https";
                    if (!d.getElementById(id)) {
                        js = d.createElement(s);
                        js.id = id;
                        js.src = p + "://platform.twitter.com/widgets.js";
                        fjs.parentNode.insertBefore(js, fjs);
                    }
                }($document[0], "script", "twitter-wjs");
            };

            /**
             * Select tab in main product detail page content part.
             */
            $scope.selectTab = function (tabName) {
                $("[id^=tabs-]").each(function () {
                    var item = $(this);
                    if (("#" + item.attr("id")) == tabName) {
                        item.removeClass("ng-hide");
                    } else {
                        item.addClass("ng-hide");
                    }
                });
                $("a[href^=#tabs-]").each(function () {
                    var item = $(this);
                    if (item.attr("href") == tabName) {
                        item.addClass("current");
                    } else {
                        item.removeClass("current");
                    }
                });
            };

            $scope.activateProductImageAnimation();
            $scope.activateSocialButtons();
            $scope.selectTab("#tabs-photos");
            MapsService.loadGoogleMaps();
        }]);
});
