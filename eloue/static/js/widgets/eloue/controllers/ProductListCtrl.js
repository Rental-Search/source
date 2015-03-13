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

            $scope.submitInProgress = false;

            /**
             * Callback function for Google maps script loaded event.
             */
            $window.googleMapsLoaded = function () {
                $("#geolocate").formmapper({
                    details: "form"
                });

                var mapCanvas = $document[0].getElementById("map-canvas"), rangeEl, radius, mapOptions, map, geocoder,
                    rangeSlider, rangeInput, rangeMax, rangeVal, notUpdateBySlider, notUpdateByMap, products;
                if (mapCanvas) {

                    $("#where").formmapper({
                        details: "form"
                    });

                    $scope.applyDatePicker("start-date");
                    $scope.applyDatePicker("end-date");

                    rangeEl = $("#range");
                    radius = Number(rangeEl.val().replace(",", "."));
                    mapOptions = {
                        zoom: MapsService.zoom(radius),
                        disableDefaultUI: true,
                        zoomControl: true,
                        mapTypeId: google.maps.MapTypeId.ROADMAP
                    };
                    map = new google.maps.Map(mapCanvas, mapOptions);
                    geocoder = new google.maps.Geocoder();
                    geocoder.geocode(
                        {address: $document[0].getElementById("where").value},
                        function (result, status) {
                            if (status === google.maps.GeocoderStatus.OK) {
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

                    // Submit form on location change.
                    var autocomplete = new google.maps.places.Autocomplete($document[0].getElementById('where'));
                    google.maps.event.addListener(autocomplete, "place_changed", function() {
                        $scope.submitForm();
                    });

                    rangeSlider = $("#range-slider");
                    if (rangeSlider) {
                        rangeInput = rangeEl;
                        rangeMax = rangeSlider.attr("max-value");
                        if (!rangeMax) {
                            $("#range-label").hide();
                        } else {
                            var updatedBySlider = false;
                            rangeVal = rangeInput.attr("value");
                            if (rangeVal) {
                                rangeSlider.attr("value", "1;" + rangeVal);
                            } else {
                                rangeSlider.attr("value", "1;" + rangeMax);
                            }
                            rangeSlider.slider({
                                from: 1,
                                to: Number(rangeMax),
                                limits: false,
                                dimension: "&nbsp;km",
                                // On mouse up submit form.
                                callback: function(value) {
                                    updatedBySlider = true;
                                    var rangeValue = value.split(";")[1];
                                    // enable the input so its value could be now posted with a form data
                                    rangeInput.prop("disabled", false);
                                    // set new values to the hidden input
                                    rangeInput.attr("value", rangeValue);
                                    // change map's zoom level
                                    map.setZoom(MapsService.zoom(rangeValue));

                                    $scope.submitForm();
                                }
                            });

                            google.maps.event.addListener(map, "zoom_changed", function () {
                                if ($scope.submitInProgress) {
                                    return;
                                }
                                if (!updatedBySlider) {
                                    var zoomLevel = map.getZoom(),
                                        calcRange = MapsService.range(zoomLevel);
                                    if (calcRange && calcRange <= rangeMax) {
                                        rangeSlider.slider("value", 1, calcRange);
                                    }
                                    rangeInput.prop("disabled", false);
                                    rangeInput.attr("value", calcRange);
                                }
                                updatedBySlider = false;
                                $scope.submitForm();
                            });
                        }
                    }

                    products = [];
                    $("li[id^='marker-']").each(function () {
                        var item = $(this),
                            product = {
                                title: item.attr("name"),
                                lat: item.attr("locationX"),
                                lng: item.attr("locationY"),
                                zIndex: Number(item.attr("id").replace("marker-", ""))
                            };
                        products.push(product);
                    });


                    $scope.setMarkers(map, products, "li#marker-");
                }
            };

            $scope.applyDatePicker = function (fieldId) {
                $("#" + fieldId).datepicker({
                    language: "fr",
                    autoclose: true,
                    todayHighlight: true,
                    startDate: Date.today()
                });
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

            $scope.activateCategoryAndSortSelector = function () {
                var detailSearchForm = $("#detail-search"), categorySelection = $("#category-selection"),
                    sortSelector = $("#sort-selector");
                if (detailSearchForm && categorySelection) {
                    categorySelection.change(function () {
                        var location = $(this).find(":selected").attr("location");
                        detailSearchForm.attr("action", location);
                    });
                }
                if (sortSelector) {
                    sortSelector.change(function (e) {
                        if (detailSearchForm) {
                            detailSearchForm.submit();
                        }
                    });
                }
                // Submit form on category change.
                categorySelection.change(function(){
                    detailSearchForm.submit();
                })
            };

            $scope.activatePriceSlider = function () {
                var priceSlider = $("#price-slider"), priceMinInput, priceMaxInput, min, max, minValue, maxValue;
                if (priceSlider) {
                    priceMinInput = $("#price-min");
                    priceMaxInput = $("#price-max");
                    min = priceSlider.attr("min-value");
                    max = priceSlider.attr("max-value");
                    if (!min || !max) {
                        $("#price-label").hide();
                    } else {
                        minValue = priceMinInput.attr("value");
                        maxValue = priceMaxInput.attr("value");
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
                            },
                            // On mouse up submit form.
                            callback: function() {
                                $scope.submitForm();
                            }
                        });
                    }
                }
            };

            $scope.setMarkers = function (map, locations, markerId) {
                var staticUrl = "/static/", scripts = $document[0].getElementsByTagName("script"), i, j, l,
                    product, image, imageHover, myLatLng, marker;
                for (i = 0, l = scripts.length; i < l; i += 1) {
                    if (scripts[i].getAttribute("data-static-path")) {
                        staticUrl = scripts[i].getAttribute("data-static-path");
                        break;
                    }
                }
                for (j = 0; j < locations.length; j += 1) {
                    product = locations[j];
                    if (markerId === "li#marker-") {
                        image = new google.maps.MarkerImage(staticUrl + "images/markers_smooth_aligned.png",
                            new google.maps.Size(26, 28),
                            new google.maps.Point(0, 28 * j),
                            new google.maps.Point(14, 28));

                        imageHover = new google.maps.MarkerImage(staticUrl + "images/markers_smooth_aligned.png",
                            new google.maps.Size(26, 28),
                            new google.maps.Point(29, 28 * j),
                            new google.maps.Point(14, 28));
                    }
                    myLatLng = new google.maps.LatLng(product.lat, product.lng);
                    marker = new google.maps.Marker({
                        position: myLatLng,
                        map: map,
                        title: product.title,
                        zIndex: product.zIndex,
                        icon: image
                    });
                    marker.set("myZIndex", marker.getZIndex());
                    google.maps.event.addListener(marker, "mouseover", $scope.mouseOverListenerGenerator(imageHover, marker, markerId));
                    google.maps.event.addListener(marker, "click", $scope.mouseClickListenerGenerator(marker, markerId));
                    google.maps.event.addListener(marker, "mouseout", $scope.mouseOutListenerGenerator(image, marker, markerId));

                    $(markerId + marker.get("myZIndex")).mouseover($scope.triggerMouseOverGenerator(marker));
                    $(markerId + marker.get("myZIndex")).mouseout($scope.triggerMouseOutGenerator(marker));
                }
            };

            $scope.mouseClickListenerGenerator = function (marker, markerId) {
                return function () {
                    // Jump to product item
                    $("html, body").animate({
                        scrollTop: $(markerId + marker.get("myZIndex")).offset().top - 20
                    }, 1000);
                };
            };

            $scope.mouseOverListenerGenerator = function (imageHover, marker, markerId) {
                return function () {
                    this.setOptions({
                        icon: imageHover,
                        zIndex: 200
                    });

                    //TODO: toggle ":hover" styles
//                $(markerId + marker.get("myZIndex")).find(".declarer-container")[0].trigger("hover");
                };
            };

            $scope.mouseOutListenerGenerator = function (image, marker, markerId) {
                return function () {
                    this.setOptions({
                        icon: image,
                        zIndex: this.get("myZIndex")
                    });
                    $(markerId + marker.get("myZIndex")).removeAttr("style");
                };
            };

            $scope.triggerMouseOverGenerator = function (marker) {
                return function () {
                    marker.setAnimation(google.maps.Animation.BOUNCE);
                    google.maps.event.trigger(marker, "mouseover");
                };
            };

            $scope.triggerMouseOutGenerator = function (marker) {
                return function () {
                    marker.setAnimation(null);
                    google.maps.event.trigger(marker, "mouseout");
                };
            };
            
            $scope.activateRenterSelect = function () {
                var particularCheckbox = $("#particular"), proCheckbox = $("#professional");
                particularCheckbox.change(
                    function(){
                        if (this.checked) {
                            proCheckbox.prop("checked", false);
                        }
                        $scope.submitForm();
                    });
                proCheckbox.change(
                    function(){
                        if (this.checked) {
                            particularCheckbox.prop("checked", false);
                        }
                        $scope.submitForm();
                    });
            };
            
            $scope.submitForm = function() {
                $("#detail-search").submit();
            };

            $scope.disableForm = function() {
                setTimeout(function() {
                    $("input, select").attr("disabled", true);
                    $(".jslider-pointer").attr("style", "display: none !important");
                    $("#submitButton").addClass("loading");
                }, 50);

            };

            $("#detail-search").on("submit", function() {
                $scope.submitInProgress = true;
                $scope.disableForm();
                return true;
            });

            MapsService.loadGoogleMaps();
            $scope.activateLayoutSwitcher();
            $scope.activateCategoryAndSortSelector();
            $scope.activatePriceSlider();
            $scope.activateRenterSelect();
        }]);
});
