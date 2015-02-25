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
        function ($scope, $window, $document, MapsService, UtilsService) {
            var map, latLngsArr = [], addHovered = false;

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
                    mapOptions, agencies;

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

                // Create markers.
                agencies = [];
                $("li[id^='marker-']").each(function () {
                    var item = $(this),
                        agency = {
                            title: item.attr('name'),
                            lat: item.attr('locationX'),
                            lng: item.attr('locationY'),
                            zIndex: Number(item.attr('id').replace('marker-', ''))
                        };
                    agencies.push(agency);
                });

                $scope.setMarkers(map, agencies, 'li#marker-');

                // Need to called to prevent wrong map drawing inside modal.
                google.maps.event.trigger(map, 'resize');

                // Center map.
                MapsService.centerMap(map, latLngsArr, {minZoom: 5, maxZoom: 16});
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

                for (j = 0; j < locations.length; j += 1) {
                    agency = locations[j];
                    if (!agency.lat || !agency.lng) {
                        continue;
                    }
                    if (markerId === 'li#marker-') {
                        image = new google.maps.MarkerImage(staticUrl + 'images/markers_smooth_aligned.png',
                            new google.maps.Size(26, 28),
                            new google.maps.Point(0, 28 * j),
                            new google.maps.Point(14, 28));

                        imageHover = new google.maps.MarkerImage(staticUrl + 'images/markers_smooth_aligned.png',
                            new google.maps.Size(26, 28),
                            new google.maps.Point(29, 28 * j),
                            new google.maps.Point(14, 28));
                    }
                    myLatLng = new google.maps.LatLng(agency.lat, agency.lng);

                    // Store markers.
                    latLngsArr.push(myLatLng);

                    marker = new google.maps.Marker({
                        position: myLatLng,
                        map: map,
                        title: agency.title,
                        zIndex: agency.zIndex,
                        icon: image
                    });
                    marker.set('myZIndex', marker.getZIndex());

                    // Add listeners.
                    google.maps.event.addListener(marker, 'mouseover', $scope.mouseOverListenerGenerator(imageHover, marker, markerId));
                    google.maps.event.addListener(marker, 'click', $scope.mouseClickListenerGenerator(marker, markerId));
                    google.maps.event.addListener(marker, 'mouseout', $scope.mouseOutListenerGenerator(image, marker, markerId));

                    $(markerId + marker.get('myZIndex')).mouseover($scope.triggerMouseOverGenerator(marker));
                    $(markerId + marker.get('myZIndex')).mouseout($scope.triggerMouseOutGenerator(marker));
                }

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

            MapsService.loadGoogleMaps();
        }]);
});