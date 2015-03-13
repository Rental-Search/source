define([
    'eloue/app',
    '../../../common/eloue/services/MapsService'
], function (EloueWidgetsApp) {
    'use strict';
    /**
     * Controller to run scripts necessary for pro shop popup.
     */
    EloueWidgetsApp.controller('ProShopCtrl', [
        '$scope',
        '$window',
        '$document',
        'MapsService',
        'UtilsService',
        'GoogleMapsMarkers',
        function ($scope, $window, $document, MapsService, UtilsService, GoogleMapsMarkers) {
            var map, latLngsArr = [], addHovered = false, mapMarker = GoogleMapsMarkers, markers;

            // On modal shown.
            $('#pro-popin-shop').on('shown.bs.modal', function () {
                if (map) {
                    // Need to called to prevent wrong map drawing inside modal.
                    google.maps.event.trigger(map, 'resize');

                    // Center map.
                    MapsService.centerMap(map, latLngsArr, {minZoom: 5, maxZoom: 16});
                }
            });

            $window.googleMapsLoaded = function () {

                var mapCanvas = $document[0].getElementById('map-canvas'),
                    mapOptions;

                if (!mapCanvas) {
                    return;
                }

                // Init the map.
                mapOptions = {
                    zoom: 5,
                    disableDefaultUI: true,
                    zoomControl: true,
                    mapTypeId: google.maps.MapTypeId.ROADMAP
                };

                map = new google.maps.Map(mapCanvas, mapOptions);

                // Init custom scrollbar.
                UtilsService.initCustomScrollbars();
                $($window).trigger('resize');

                $scope.addMarkers();
            };

            $scope.addMarkers = function() {
                // Create markers.
                var agencies = [];
                latLngsArr = [];
                markers = [];
                $("li[id^='marker-']").each(function (index) {
                    var item = $(this),
                        agency = {
                            title: item.attr('name'),
                            lat: item.attr('locationX'),
                            lng: item.attr('locationY'),
                            zIndex: Number(item.attr('id').replace('marker-', '')),
                            markerIndex: index + 1
                        };
                    // Add markers only for visible list items.
                    if (!item.hasClass("ng-hide")) {
                        agencies.push(agency);
                    }
                });

                $scope.setMarkers(map, agencies, 'li#marker-');

                // Need to called to prevent wrong map drawing inside modal.
                google.maps.event.trigger(map, 'resize');

                // Center map.
                MapsService.centerMap(map, latLngsArr, {minZoom: 5, maxZoom: 16});
            };

            /**
             * Delete markers from map.
             */
            $scope.deleteMarkers = function() {
                for (var i = 0; i < markers.length; i++) {
                    markers[i].setMap(null);
                }
            };

            $scope.setMarkers = function (map, locations, markerId) {
                var staticUrl = '/static/', scripts = $document[0].getElementsByTagName('script'), i, j, l,
                    agency, image, imageHover, myLatLng, marker;
                for (i = 0, l = scripts.length; i < l; i += 1) {
                    if (scripts[i].getAttribute('data-static-path')) {
                        staticUrl = scripts[i].getAttribute('data-static-path');
                        break;
                    }
                }

                var svgTemplate = mapMarker.template;

                for (j = 0; j < locations.length; j += 1) {
                    agency = locations[j];
                    if (!agency.lat || !agency.lng) {
                        continue;
                    }

                    if (markerId === 'li#marker-') {
                        // Create svg marker according to label number (for values 10 and greater wide marker is used).
                        image = $scope.createMarker(svgTemplate, mapMarker.unselected, mapMarker.unselectedLarge, agency.markerIndex);
                        imageHover = $scope.createMarker(svgTemplate, mapMarker.selected, mapMarker.selectedLarge, agency.markerIndex);
                    }
                    myLatLng = new google.maps.LatLng(agency.lat, agency.lng);

                    // Store markers.
                    latLngsArr.push(myLatLng);

                    marker = new google.maps.Marker({
                        position: myLatLng,
                        map: map,
                        draggable: false,
                        raiseOnDrag: false,
                        title: agency.title,
                        zIndex: agency.zIndex,
                        icon: image
                    });
                    marker.set('myZIndex', marker.getZIndex());

                    markers.push(marker);

                    //Add listeners.
                    google.maps.event.addListener(marker, 'mouseover', $scope.mouseOverListenerGenerator(imageHover, marker, markerId));
                    google.maps.event.addListener(marker, 'click', $scope.mouseClickListenerGenerator(marker, markerId));
                    google.maps.event.addListener(marker, 'mouseout', $scope.mouseOutListenerGenerator(image, marker, markerId));

                    $(markerId + marker.get('myZIndex')).mouseover($scope.triggerMouseOverGenerator(marker));
                    $(markerId + marker.get('myZIndex')).mouseout($scope.triggerMouseOutGenerator(marker));
                }
            };

            $scope.createMarker = function(svgTemplate, marker, wideMarker, index) {
                var markerSvg = index < 10 ? svgTemplate.replace('{{mapMarker}}', marker) : svgTemplate.replace('{{mapMarker}}', wideMarker);
                markerSvg = markerSvg.replace("{{markerLabel}}", "" + (index));
                return {url: URL.createObjectURL(new Blob([markerSvg], {type: 'image/svg+xml'})), anchor: new google.maps.Point(13, 27)};
            };

            $scope.mouseOverListenerGenerator = function (imageHover, marker, markerId) {
                return function () {
                    this.setOptions({
                        icon: imageHover,
                        zIndex: 200
                    });
                    if (addHovered) {
                        $(markerId + marker.get('myZIndex') + ' > .section-body').addClass('hovered');
                    }
                };
            };

            $scope.mouseOutListenerGenerator = function (image, marker, markerId) {
                return function () {
                    this.setOptions({
                        icon: image,
                        zIndex: this.get('myZIndex')
                    });
                    if (addHovered) {
                        $(markerId + marker.get('myZIndex') + '> .section-body').removeClass('hovered');
                    }
                };
            };

            $scope.triggerMouseOverGenerator = function (marker) {
                return function () {
                    // Prevent list item highlighting on item hover.
                    addHovered = false;

                    marker.setAnimation(google.maps.Animation.BOUNCE);
                    google.maps.event.trigger(marker, 'mouseover');
                };
            };

            $scope.triggerMouseOutGenerator = function (marker) {
                return function () {
                    addHovered = true;
                    marker.setAnimation(null);
                    google.maps.event.trigger(marker, 'mouseout');
                };
            };

            $scope.mouseClickListenerGenerator = function (marker, markerId) {
                return function () {
                    $('.scrollbar-custom').mCustomScrollbar('scrollTo', markerId + marker.get('myZIndex'), {
                        scrollInertia: 300
                    });
                };
            };

            // On key up in the search field, filter visible agencies according to city.
            $("#cityInput").on("keyup", function() {
                console.log($scope.search);
                $("li[id^='marker-']").each(function () {
                    var item = $(this);
                    if (item.attr('city').trim().startsWith($scope.search.trim(), true)) {
                        // Show item.
                        item.removeClass("ng-hide");
                    }
                    else {
                        // Hide item.
                        item.addClass("ng-hide");
                    }
                });

                // Redraw markers on the map.
                $scope.deleteMarkers();
                $scope.addMarkers();
            });

            if (typeof String.prototype.startsWith != 'function') {
                String.prototype.startsWith = function(str, ignoreCase) {
                    return (ignoreCase ? this.toUpperCase() : this)
                            .indexOf(ignoreCase ? str.toUpperCase() : str) == 0;
                };
            }

            MapsService.loadGoogleMaps();
        }]);
});