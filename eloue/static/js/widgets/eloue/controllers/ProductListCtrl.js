define([
    "eloue/app",
    "../../../common/eloue/services/MapsService",
    "algoliasearch-helper"
], function (EloueWidgetsApp, MapsService, algoliasearchHelper) {
    "use strict";
    /* 
     * http://ericclemmons.com/angular/angular-trust-filter/
     */
    EloueWidgetsApp.filter('trust', [
      '$sce',
      function($sce) {
        return function(text, type) {
          // Defaults to treating trusted text as `html`
          return $sce.trustAs(type || 'html', text);
        }
      }
    ]);
    
    /**
     * Controller to run scripts necessary for product list page.
     */
    EloueWidgetsApp.controller("ProductListCtrl", [
        "$scope",
        "$window",
        "$document",
        "MapsService",
        "algolia",
        "$log",
        function ($scope, $window, $document, MapsService, algolia, $log) {
           
            $scope.searchResultsPerPage = 12;
            
            
            /* 
             * Algolia config 
             * */
            
            var SEARCH_PARAMETERS = {
                hierarchicalFacets: [{
                    name: 'category',
                    attributes: ['algolia_categories.lvl0',
                                 'algolia_categories.lvl1',
                                 'algolia_categories.lvl2'],
                    sortBy: ['count:desc', 'name:asc']
                }],
                disjunctiveFacets: ["pro_owner",
                                    "price"],
                hitsPerPage: $scope.searchResultsPerPage
            };
            
            var client = algolia.Client('F2G181ROXT', '1892770732420446ef9165ec76bdbdbd');
            
            $scope.search_ordering = "-created_at";
            
            $scope.search_index = 'e-loue-test-geo-multilvl-products.product';
            
            $scope.search = algoliasearchHelper(client, $scope.search_index, SEARCH_PARAMETERS);
            
            
            /* 
             * Filter refinement 
             * */
            
            $scope.refinePrices = function(sliderId){
                
                var state = $scope.search.getState();
                var newVal, oldVal;
                
                newVal = $scope.price_slider.min;
                if (state.isNumericRefined("price", '>=')){
                    oldVal = state.getNumericRefinement("price", '>=')[0];
                    if (oldVal != newVal) {
                        $scope.search.removeNumericRefinement("price", '>=');
                        $scope.search.addNumericRefinement("price", '>=', newVal);
                    }
                } else {
                    $scope.search.addNumericRefinement("price", '>=', newVal);
                }
                
                newVal = $scope.price_slider.max;
                if (state.isNumericRefined("price", '<=')){
                    oldVal = state.getNumericRefinement("price", '<=')[0];
                    if (oldVal != newVal) {
                        $scope.search.removeNumericRefinement("price", '<=');
                        $scope.search.addNumericRefinement("price", '<=', newVal);
                    }
                } else {
                    $scope.search.addNumericRefinement("price", '<=', newVal);
                }
                
                $scope.submitForm();
                
            };
            
            $scope.refineRenterPart = function(newVal){
                var state = $scope.search.getState();
                if (newVal && !state.isDisjunctiveFacetRefined("pro_owner", false)){
                    $scope.search.addDisjunctiveFacetRefinement("pro_owner", false);
                }
                if (!newVal && state.isDisjunctiveFacetRefined("pro_owner", false)){
                    $scope.search.removeDisjunctiveFacetRefinement("pro_owner", false);
                }
                $scope.search.search();
            };
            
            $scope.refineRenterPro = function(newVal){
                var state = $scope.search.getState();
                if (newVal && !state.isDisjunctiveFacetRefined("pro_owner", true)){
                    $scope.search.addDisjunctiveFacetRefinement("pro_owner", true);
                }
                if (!newVal && state.isDisjunctiveFacetRefined("pro_owner", true)){
                    $scope.search.removeDisjunctiveFacetRefinement("pro_owner", true);
                }
                $scope.search.search();
            };
            
            $scope.refineCategory = function(path) {
                $scope.search.toggleRefinement("category", path).search();
            };
            
            
            /*
             * Pagination & ordering 
             */
            
            $scope.nextPage = function(){
                $log.debug("Going to next page");
                $scope.setPage(Math.min($scope.page + 1, $scope.pages_count-1));
            };

            $scope.prevPage = function(){
                $log.debug("Going to prev page");
                $scope.setPage(Math.max(0, $scope.page - 1));
            };
            
            $scope.setPage = function(page){
                $log.debug("Going to page " + page);
                $scope.searchPage = page;
                $scope.submitForm();
            };
            
            $scope.setOrdering = function(ordering){
                $scope.search
                    .setIndex(!!ordering ? $scope.search_index+"_"+ordering : $scope.search_index)
                    .search();
            };
            
            
            /* 
             * Filter rendering
             * */
            
            $scope.renderPagination = function(result){
                $scope.page = Math.min(result.nbPages-1, Math.max(0, result.page));
                var WINDOW_SIZE = 9;
                if (result.nbPages < WINDOW_SIZE){
                    $scope.pages_range = new Array(result.nbPages);
                    for (var i=0; i<result.nbPages; i++){
                        $scope.pages_range[i] = i;
                    }
                } else {
                    if ($scope.page > result.nbPages/2){
                        var last = Math.min(result.page+Math.ceil(WINDOW_SIZE/2), result.nbPages);    
                        var first = Math.max(0, last-WINDOW_SIZE);
                    } else {
                        var first = Math.max(0, result.page-Math.floor(WINDOW_SIZE/2));
                    }
                    $scope.pages_range = new Array(WINDOW_SIZE);
                    for (var i=0; i<WINDOW_SIZE; i++){
                        $scope.pages_range[i] = first + i;
                    }
                }
            };
            
            $scope.renderPriceSlider = function(result, state){
                
                var facetResult = result.getFacetByName("price");
                var ref;
                var statsMin = facetResult.stats.min, statsMax = facetResult.stats.max;
                
                $scope.price_slider.options.floor = $scope.price_slider.min = statsMin;
                if (state.isNumericRefined("price", '>=')){
                    ref = state.getNumericRefinement("price", '>=')[0];
                    $scope.price_slider.min = Math.max(statsMin, ref);
                }
                
                $scope.price_slider.options.ceil = $scope.price_slider.max = statsMax;
                if (state.isNumericRefined("price", '<=')){
                    ref = state.getNumericRefinement("price", '<=')[0];
                    $scope.price_slider.max = Math.min(statsMax, ref);
                }
                
            };

            $scope.renderRangeSlider = function(result){
                
            };
            
            $scope.renderSearchCategories = function(result){
                if (result.hierarchicalFacets && result.hierarchicalFacets[0]) {
                    $scope.category = result.hierarchicalFacets[0];    
                }
            };
                       
            $scope.renderBreadcrumbs = function(state) {
//                $scope.search_breadcrumbs = state.getHierarchicalFacetBreadcrumb("category");
            };
            
            $scope.renderRenterTypes = function(result, state){
                var facetResult = result.getFacetByName("pro_owner");
                $scope.search_pro_count = ('true' in facetResult.data ? facetResult.data.true : 0);
                $scope.search_part_count = ('false' in facetResult.data ? facetResult.data.false : 0);
//                $scope.search_pro = state.isDisjunctiveFacetRefined("pro_owner", true);
//                $scope.search_part = state.isDisjunctiveFacetRefined("pro_owner", false);
            };
            
            /* 
             * Process search results 
             * */
            
            $scope.processResult = function(result, state){
                $log.debug(result);
                $scope.search_result_count = result.nbHits;

                $log.debug($scope.search_pro+' '+state.isDisjunctiveFacetRefined("pro_owner", true));
                $log.debug($scope.search_part+' '+state.isDisjunctiveFacetRefined("pro_owner", false));
                
                if ($scope.search_result_count){
                    $scope.search_results = result.hits;
                    
//                    $scope.price_slider.options.min = Math.min($scope.price_slider.min, result.facets_stats.price.min);
//                    $scope.price_slider.options.max = Math.max($scope.price_slider.max, result.facets_stats.price.max);
                    
                    $scope.pages_count = result.nbPages;
                    $scope.results_per_page = result.hitsPerPage;
                    $scope.page = result.page;
                    
                    //$scope.renderResults(result);
                    $scope.renderPagination(result);
                    $scope.renderSearchCategories(result);
                    $scope.renderPriceSlider(result, state);
                    $scope.renderBreadcrumbs(state);
                    $scope.renderRenterTypes(result, state);
//                    $log.debug($scope.search.getHierarchicalFacetBreadcrumb("category"));
                    
//                    $scope.renderRangeSlider(result);
                    
                    
//                    $scope.updatePriceSlider();
                    
//                    $log.debug("Query: " + $scope.search_query);
////                    $log.debug("Query params: ");
////                    $log.debug(params);
//                    $log.debug("X, Y, R: " + $scope.search_cordinates+ " " + $scope.search_radius);
//                    $log.debug("Hits count: " + $scope.search_result_count);
//                    $log.debug("Price: " + $scope.price_from + " to " + $scope.price_to);
//                    $log.debug("Pro: " + $scope.search_pro);
//                    $log.debug("Pages count: "+$scope.pages_count);
//                    $log.debug("Pages range: "+$scope.pages_range);
                } else {
                    $log.debug("No results");
                }
                
                $scope.$apply();
                
                $window.googleMapsLoaded();
            };
            
            $scope.processError = function(error){
                $log.debug(error);
            };
            
            $scope.search.on('result', $scope.processResult)
                .on('error', $scope.processError);
            
            
            $scope.resetQuery = function(){
                $scope.search_query = "";
            };
            
            $scope.resetFilters = function(){
                
            };
            
            $scope.submitInProgress = false;
            
            $scope.search_location = "";
            $scope.search_results = [];
            $scope.searchPage = 0;
            $scope.search_result_count = 0;
            $scope.search_results_price_max = 1000;
            $scope.search_results_price_min = 0;
            $scope.price_from = 0;
            $scope.price_to = 1000;
            $scope.search_pro = false;
            $scope.search_part = false;
            $scope.search_pro_count = 0;
            $scope.search_part_count = 0;
            $scope.price_slider = {
                min: 0,
                max: 1000,
                options: {
                    floor: 0,
                    ceil: 1000,
                    onEnd: $scope.refinePrices
                }
            };
            

            /**
             * Callback function for Google maps script loaded event.
             */
            $window.googleMapsLoaded = function () {
                
                $log.debug("Google maps loaded");
                
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
                                $log.debug("Location: " + result[0].geometry.location);
                                $scope.search_cordinates = result[0].geometry.location;
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
                                    
                                    $scope.search_radius = rangeValue;
                                    
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
                        $log.debug(product);
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
//                if (detailSearchForm && categorySelection) {
//                    categorySelection.change(function () {
//                        var location = $(this).find(":selected").attr("location");
//                        var location = $(this).find(":selected").attr("value");
////                        $scope.category = location;
//                        $log.debug("Category: "+$scope.category);
//                        detailSearchForm.attr("action", location);
//                    });
//                }
                if (sortSelector) {
                    sortSelector.change(function (e) {
                        if (detailSearchForm) {
//                            $scope.submitForm();
                            $scope.newSearch();
//                            detailSearchForm.submit();
                        }
                    });
                }
                // Submit form on category change.
//                categorySelection.change(function(){
////                    $scope.submitForm();
//                    $scope.newSearch();
////                    detailSearchForm.submit();
//                })
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
                                
                                $scope.price_from = values[0];
                                $scope.price_to = values[1];
                                
                            },
                            // On mouse up submit form.
                            callback: function() {
                                $scope.submitForm();
                            }
                        });
                    }
                }
            };

            $scope.updatePriceSlider = function(){
                var priceSlider = $("#price-slider");
                priceSlider.slider("option", "min", $scope.search_results_price_min);
                priceSlider.slider("option", "max", $scope.search_results_price_max);    
                $log.debug("Price: "+$scope.search_results_price_min+' - '+$scope.search_results_price_max);
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

                var markersUrl = staticUrl + "images/markers_smooth_aligned.png";

                var mapCanvas= $("#map-canvas");

                var markerFilename = mapCanvas.attr('markers-filename');
                if (markerFilename) {
                    markersUrl = staticUrl + "images/" + markerFilename;
                }

                var markerHeight = 28;

                var markerHeightAttr = mapCanvas.attr('marker-height');
                if (markerHeightAttr) {
                    markerHeight = parseInt(markerHeightAttr);
                }



                for (j = 0; j < locations.length; j += 1) {
                    product = locations[j];
                    if (markerId === "li#marker-") {
                        image = new google.maps.MarkerImage(markersUrl,
                            new google.maps.Size(26, markerHeight),
                            new google.maps.Point(0, markerHeight * j),
                            new google.maps.Point(14, markerHeight));

                        imageHover = new google.maps.MarkerImage(markersUrl,
                            new google.maps.Size(26, markerHeight),
                            new google.maps.Point(29, markerHeight * j),
                            new google.maps.Point(14, markerHeight));
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
                            $scope.search_pro = false;
                        }
                        $scope.submitForm();
                    });
                proCheckbox.change(
                    function(){
                        if (this.checked) {
                            particularCheckbox.prop("checked", false);
                            $scope.search_pro = true;
                        }
                        $scope.submitForm();
                    });
            };
            
            $scope.submitForm = function() {
                
                $scope.search.setQuery($scope.search_query)
                    .setCurrentPage($scope.searchPage)
                    .search();
                
            };

            $scope.newSearch = function(){
                $scope.searchPage = 0;
                $scope.submitForm();
            }
            

            
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
//            $scope.activateRenterSelect();
//            $scope.submitForm();
        }]);
});
