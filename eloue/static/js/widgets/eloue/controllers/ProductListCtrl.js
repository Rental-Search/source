define([
    "eloue/app",
    "../../../common/eloue/services/MapsService"
], function (EloueWidgetsApp) {
    "use strict";

    /**
     * Controller to run scripts necessary for product list page.
     */
    EloueWidgetsApp.controller("ProductListCtrl", [
        "$scope",
        "$window",
        "$document",
        "MapsService",
        function ($scope, $window, $document, MapsService) {

            $window.googleMapsLoaded = function () {
                $("#geolocate").formmapper({
                    details: "form"
                });

                var mapCanvas = $document[0].getElementById("map-canvas");
                if (mapCanvas) {

                    $("#where").formmapper({
                        details: "form"
                    });

                    $("#start-date").datepicker({
                        language: "fr",
                        autoclose: true,
                        todayHighlight: true,
                        startDate: Date.today()
                    });

                    $("#end-date").datepicker({
                        language: "fr",
                        autoclose: true,
                        todayHighlight: true,
                        startDate: Date.today()
                    });

                    var rangeEl = $("#range");
                    var radius = Number(rangeEl.val().replace(",", "."));
                    var mapOptions = {
                        zoom: MapsService.zoom(radius),
                        disableDefaultUI: true,
                        zoomControl: true,
                        mapTypeId: google.maps.MapTypeId.ROADMAP
                    };
                    var map = new google.maps.Map(mapCanvas, mapOptions);
                    var geocoder = new google.maps.Geocoder();
                    geocoder.geocode(
                        {address: $document[0].getElementById("where").value},
                        function (result, status) {
                            if (status == google.maps.GeocoderStatus.OK) {
                                map.setCenter(result[0].geometry.location);
                                var circle = new google.maps.Circle({
                                    map: map,
                                    radius: radius * 1000,
                                    fillColor: "#FFFFFF",
                                    editable: false
                                });
                            }
                        }
                    );

                    var rangeSlider = $("#range-slider");
                    if (rangeSlider) {
                        var rangeInput = rangeEl;
                        var rangeMax = rangeSlider.attr("max-value");
                        if (!rangeMax) {
                            $("#range-label").hide();
                        } else {
                            var rangeVal = rangeInput.attr("value");
                            if (rangeVal) {
                                rangeSlider.attr("value", "1;" + rangeVal);
                            } else {
                                rangeSlider.attr("value", "1;" + rangeMax);
                            }

                            var notUpdateBySlider = false, notUpdateByMap = false;
                            rangeSlider.slider({
                                from: 1,
                                to: Number(rangeMax),
                                limits: false,
                                dimension: "&nbsp;km",
                                onstatechange: function (value) {
                                    notUpdateByMap = true;
                                    if (!notUpdateBySlider) {
                                        var range_value = value.split(";")[1];
                                        // enable the input so its value could be now posted with a form data
                                        rangeInput.prop("disabled", false);
                                        // set new values to the hidden input
                                        rangeInput.attr("value", range_value);
                                        // change map's zoom level
                                        map.setZoom(MapsService.zoom(range_value));
                                    }
                                    setTimeout(function () {
                                        notUpdateByMap = false;
                                    }, 1000);
                                }
                            });

                            google.maps.event.addListener(map, "zoom_changed", function () {
                                notUpdateBySlider = true;
                                if (!notUpdateByMap) {
                                    var zoomLevel = map.getZoom();
                                    var calcRange = MapsService.range(zoomLevel);
                                    if (calcRange && calcRange <= rangeMax) {
                                        rangeSlider.slider("value", 1, calcRange);
                                    }
                                }
                                setTimeout(function () {
                                    notUpdateBySlider = false;
                                }, 1000);
                            });
                        }
                    }

                    var products = [];
                    $("li[id^='marker-']").each(function () {
                        var item = $(this);
                        var product = {
                            title: item.attr("name"),
                            lat: item.attr("locationX"),
                            lng: item.attr("locationY"),
                            zIndex: Number(item.attr("id").replace("marker-", ""))
                        };
                        products.push(product);
                    });


                    setMarkers(map, products, "li#marker-");
                }
            };

            $scope.activateLayoutSwitcher = function () {
                var layoutSwitcher = $(".layout-switcher"), article = $("article");
                if (layoutSwitcher && article) {
                    // switch grid/list layouts
                    $(layoutSwitcher).on("click", "i", function () {
                        if ($(this).hasClass("grid")) {
                            article.removeClass("list-layout");
                            article.addClass("grid-layout");
                        } else {
                            article.removeClass("grid-layout");
                            article.addClass("list-layout");
                        }
                    });
                }
            };

            var detailSearchForm = $("#detail-search");

            var categorySelection = $("#category-selection");
            if (detailSearchForm && categorySelection) {
                categorySelection.change(function () {
                    var location = $(this).find(":selected").attr("location");
                    detailSearchForm.attr("action", location);
                });
            }

            var priceSlider = $("#price-slider");
            if (priceSlider) {
                var priceMinInput = $("#price-min"), priceMaxInput = $("#price-max");
                var min = priceSlider.attr("min-value");
                var max = priceSlider.attr("max-value");
                if (!min || !max) {
                    $("#price-label").hide();
                } else {
                    var minValue = priceMinInput.attr("value"), maxValue = priceMaxInput.attr("value");
                    if (!minValue) {
                        minValue = min;
                    }
                    if (!maxValue) {
                        maxValue = max;
                    }
                    priceSlider.attr("value", minValue + ";" + maxValue);
                    priceSlider.slider({
                        from: Number(min),
                        to: Number(max),
                        limits: false,
                        dimension: "&nbsp;&euro;",
                        onstatechange: function (value) {
                            var values = value.split(";");
                            // enable inputs so their values could be now posted with a form data
                            priceMinInput.prop("disabled", false);
                            priceMaxInput.prop("disabled", false);
                            // set new values to hidden inputs
                            priceMinInput.attr("value", values[0]);
                            priceMaxInput.attr("value", values[1]);
                        }
                    });
                }
            }

            var sortSelector = $("#sort-selector");
            if (sortSelector) {
                sortSelector.change(function (e) {
                    if (detailSearchForm) {
                        detailSearchForm.submit();
                    }
                });
            }


            var setMarkers = function (map, locations, markerId) {
                var staticUrl = "/static/";
                var scripts = $document[0].getElementsByTagName("script");
                for (var i = 0, l = scripts.length; i < l; i++) {
                    if (scripts[i].getAttribute("data-static-path")) {
                        staticUrl = scripts[i].getAttribute("data-static-path");
                        break;
                    }
                }
                for (var j = 0; j < locations.length; j++) {
                    var product = locations[j];

                    var image, imageHover;

                    if (markerId == "li#marker-") {
                        image = new google.maps.MarkerImage(staticUrl + "images/markers_smooth_aligned.png",
                            new google.maps.Size(26, 28),
                            new google.maps.Point(0, 28 * j),
                            new google.maps.Point(14, 28));

                        imageHover = new google.maps.MarkerImage(staticUrl + "images/markers_smooth_aligned.png",
                            new google.maps.Size(26, 28),
                            new google.maps.Point(29, 28 * j),
                            new google.maps.Point(14, 28));
                    }

                    var myLatLng = new google.maps.LatLng(product.lat, product.lng);

                    var marker = new google.maps.Marker({
                        position: myLatLng,
                        map: map,
                        title: product.title,
                        zIndex: product.zIndex,
                        icon: image
                    });

                    marker.set("myZIndex", marker.getZIndex());

                    google.maps.event.addListener(marker, "mouseover", mouseOverListenerGenerator(imageHover, marker, markerId));
                    google.maps.event.addListener(marker, "click", mouseClickListenerGenerator(marker, markerId));
                    google.maps.event.addListener(marker, "mouseout", mouseOutListenerGenerator(image, marker, markerId));

                    $(markerId + marker.get("myZIndex")).mouseover(triggerMouseOverGenerator(marker));

                    $(markerId + marker.get("myZIndex")).mouseout(triggerMouseOutGenerator(marker));
                }
            };

            function mouseClickListenerGenerator(marker, markerId) {
                return function () {
                    // Jump to product item
                    $("html, body").animate({
                        scrollTop: $(markerId + marker.get("myZIndex")).offset().top - 20
                    }, 1000);
                };
            }

            function mouseOverListenerGenerator(imageHover, marker, markerId) {
                return function () {
                    this.setOptions({
                        icon: imageHover,
                        zIndex: 200
                    });

                    //TODO: toggle ":hover" styles
//                $(markerId + marker.get("myZIndex")).find(".declarer-container")[0].trigger("hover");
                };
            }

            function mouseOutListenerGenerator(image, marker, markerId) {
                return function () {
                    this.setOptions({
                        icon: image,
                        zIndex: this.get("myZIndex")
                    });
                    $(markerId + marker.get("myZIndex")).removeAttr("style");
                };
            }

            function triggerMouseOverGenerator(marker) {
                return function () {
                    marker.setAnimation(google.maps.Animation.BOUNCE);
                    google.maps.event.trigger(marker, "mouseover");
                };
            }

            function triggerMouseOutGenerator(marker) {
                return function () {
                    marker.setAnimation(null);
                    google.maps.event.trigger(marker, "mouseout");
                };
            }

            MapsService.loadGoogleMaps();

            $scope.activateLayoutSwitcher();
        }]);
});
