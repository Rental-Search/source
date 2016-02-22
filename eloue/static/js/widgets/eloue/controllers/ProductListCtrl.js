define([
    "eloue/app",
//    "../../../common/eloue/services/MapsService",
    "../../../common/eloue/services/UtilsService",
    "algoliasearch-helper"
], function (EloueWidgetsApp, UtilsService, algoliasearchHelper) {
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
    
    EloueWidgetsApp.config(['uiGmapGoogleMapApiProvider', function(uiGmapGoogleMapApiProvider) {
        uiGmapGoogleMapApiProvider.configure({
            v: '3.exp',
            libraries: 'places',
            language: 'fr-FR',
            region: 'FR',
            key: 'AIzaSyD3LwG42VzGikefts9fR1AfbhmQmeRLHvU'
        });
    }]);
    
    EloueWidgetsApp.constant("SearchConstants", {
        MASTER_INDEX: 'e-loue_products.product',
        PARAMETERS: {
            hierarchicalFacets: [{
                name: 'category',
                attributes: ['algolia_categories.lvl0',
                             'algolia_categories.lvl1',
                             'algolia_categories.lvl2'],
                sortBy: ['count:desc', 'name:asc']
            }],
            disjunctiveFacets: ["pro_owner",
                                "price"],
            hitsPerPage: 12,
            aroundLatLng:"46.2,2.2",
            aroundRadius:1000000
        },
        ALGOLIA_PREFIX: "sp_",
        ALGOLIA_APP_ID: 'NSV6X2HQLR',
        ALGOLIA_KEY:'1f470a5fbfd05ca06ac97a01bca6a4eb',
        URL_PARAMETERS: ['query', 'attribute:*', 'index', 'page', 'hitsPerPage', 'aroundLatLng', 'aroundRadius'],
        DEFAULT_ORDERING: "-created_at",
        WINDOW_SIZE: 10,
        COUNTRIES: {
          'fr': {
            center: {latitude: 46.2, longitude: 2.2},
            radius: 1000
          }
        }
    });
    
    /**
     * Controller to run scripts necessary for product list page.
     */
    EloueWidgetsApp.controller("ProductListCtrl", [
        "$scope",
        "$window",
        "$timeout",
        "$document",
        "$location",
        "$log",
        "UtilsService",
        "SearchConstants",
        "uiGmapGoogleMapApi",
        "uiGmapIsReady",
        "algolia",
        function ($scope, $window, $timeout, $document, $location, $log, 
                UtilsService, SearchConstants, uiGmapGoogleMapApi, uiGmapIsReady, algolia) {
           
            $scope.search_max_range = 1000;
            $scope.country = 'fr';
            
            /* 
             * Algolia config 
             */
            var client = algolia.Client(SearchConstants.ALGOLIA_APP_ID, SearchConstants.ALGOLIA_KEY);
            $scope.search_ordering = SearchConstants.DEFAULT_ORDERING;
            $scope.search_index = SearchConstants.MASTER_INDEX;
            $scope.search = algoliasearchHelper(client, $scope.search_index, SearchConstants.PARAMETERS);
            $scope.search_default_state = $scope.search.getState();
            
            $scope.search.addDisjunctiveFacetRefinement("pro_owner", true);
            $scope.search.addDisjunctiveFacetRefinement("pro_owner", false);
            
            /*
             * Map config
             */
            $scope.map = {
                loaded: false,
                zoom: UtilsService.zoom(SearchConstants.COUNTRIES[$scope.country].radius),
                center: SearchConstants.COUNTRIES[$scope.country].center,
                options:{
                    disableDefaultUI: true,
                    zoomControl: true
                },
                events: {
                    idle: function(){
                        $log.debug('== idle ==');
                        $log.debug($scope.map.center);
                        $log.debug($scope.map.zoom);
                        $log.debug($scope.boundsChangedByRender);
                        if ($scope.boundsChangedByRender){
                            $scope.boundsChangedByRender = false;
                        } else {
                            $log.debug(UtilsService.range($scope.map.zoom));
                            var gmap = $scope.map.control.getGMap();
                            var center = gmap.getCenter();
                            $log.debug(center.toString());
                            var zoom = gmap.getZoom();
                            $scope.search.setQueryParameter('aroundLatLng', center.lat()+','+center.lng());
                            $scope.search.setQueryParameter('aroundRadius', UtilsService.range(zoom) * 1000);
                            $scope.submitForm();
                        }
                    }
                },
                control: {}
            };
            
            $scope.refineRange = function(sliderid){
                $scope.search.setQueryParameter('aroundRadius', $scope.range_slider.max * 1000);
                $scope.submitForm();
            };
            

            function algoliaCoords(point){
                return point.latitude + ',' + point.longitude;
            };
            
            function angularGmapCords(point){
                var arr = point.split(',');
                return {latitude:parseFloat(arr[0]), longitude:parseFloat(arr[1])};
            };
            

            $scope.rangeUpdatedBySlider = false;
            
            // On map loaded
            uiGmapGoogleMapApi.then(function(maps) {

                var placeInputHead = $document[0].getElementById('geolocate');
                $scope.search_location = placeInputHead.value;
                
                var ac_params = {
                    componentRestrictions: {country: 'fr'},
                    types: ['geocode']
                };
                
                var autocomplete_head = new maps.places.Autocomplete(placeInputHead,ac_params);
                
                uiGmapIsReady.promise(1).then(function(instances) {
                    instances.forEach(function(inst) {
                        var map = inst.map;
                       
                        $scope.refineLocationByPlace = function(place){
//                            $log.debug('refineLocationByPlace');
                            $scope.search_location = place.name;
                            map.fitBounds(place.geometry.viewport);

                        };

                        $scope.map.options.mapTypeId = maps.MapTypeId.ROADMAP;
                        
                        // TODO bounds are used for the search, but dragend, zoom changed and center_changed do not guarantee that bounds changes will be available
                        
//                        map.addListener("idle", function () {
//                            $log.debug("idle");
//                            $scope.refineLocationByMap();
//                        });
                        
                        var autocompleteChangeListener = function(autocomplete) {
                            return function(){
                                var place = autocomplete.getPlace();
                                
                                $scope.refineLocationByPlace(place);
                            };
                        };
                        autocomplete_head.addListener('place_changed', autocompleteChangeListener(autocomplete_head));
//                        autocomplete_aside.addListener('place_changed', autocompleteChangeListener(autocomplete_aside));
                        
                        
                    });
                    
                    
                });
                
                $scope.get_marker_images = function(){
                    
                    const MARKER_IMAGE_COUNT = 19;
                    
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
                    
                    var imgs = [];
                    
                    for (var i=0; i<MARKER_IMAGE_COUNT; i++){
                        imgs.push({
                            normal: new maps.MarkerImage(markersUrl,
                                    new maps.Size(26, markerHeight),
                                    new maps.Point(0, markerHeight * i),
                                    new maps.Point(14, markerHeight)),
                            hover: new google.maps.MarkerImage(markersUrl,
                                    new maps.Size(26, markerHeight),
                                    new maps.Point(29, markerHeight * i),
                                    new maps.Point(14, markerHeight)) 
                        });
                    };
                    
                    return imgs;
                };
                
                $scope.marker_images = $scope.get_marker_images();
                
                const SW_LAT=0, SW_LNG=1, NE_LAT=2, NE_LNG=3;
                
                $scope.renderMap = function(result, state) {
                    
                    $scope.boundsChangedByRender = true;
                    
                    $log.debug('== renderMap ==');
                    
                    for (var ri=0; ri<$scope.product_list.length; ri++){
                        var res = $scope.product_list[ri];
                        res.location_obj = {latitude: res.locations[0], longitude: res.locations[1]};
                        res.images = $scope.marker_images[ri];
                        res.markerId = ri;
                        res.markerOptions = {
                            icon: res.images.normal,
                            title: res.summary,
                            zIndex: ri
                        };
                        
                    };
                    var gmap = $scope.map.control.getGMap();
                    
                    $log.debug(state.getQueryParameter('aroundLatLng'));
                    $log.debug(state.getQueryParameter('aroundRadius'));
                    
                    $scope.map.center = angularGmapCords(state.getQueryParameter('aroundLatLng'));
                    var radius = parseFloat(state.getQueryParameter('aroundRadius'))/1000;
                    $scope.map.zoom = UtilsService.zoom(radius);
                    $scope.range_slider.max = radius;
                    
                };
                
                
                $scope.marker_event_handlers = {
                    mouseover: function(marker, eventName, model, args){
                        marker.setOptions({
                            icon: model.images.hover,
                            zIndex: 200
                        });
                    },
                    click: function(marker, eventName, model, args){
                        $("html, body").animate({
                            scrollTop: $("li#marker-" + model.markerId).offset().top - 20
                        }, 1000);
                    },
                    mouseout: function(marker, eventName, model, args){
                        marker.setOptions({
                            icon: model.images.normal,
                            zIndex: parseInt(model.markerId) // TODO remove parseInt
                        });
                    }
                };
                
//                $scope.triggerMouseOverGenerator = function (marker) {
//                    return function () {
//                        marker.setAnimation(google.maps.Animation.BOUNCE);
//                        google.maps.event.trigger(marker, "mouseover");
//                    };
//                };
//
//                $scope.triggerMouseOutGenerator = function (marker) {
//                    return function () {
//                        marker.setAnimation(null);
//                        google.maps.event.trigger(marker, "mouseout");
//                    };
//                };
                
                $scope.map.loaded = true;

            });
            
            

            
            
            /* 
             * Filter refinement 
             */
            
            $scope.onLocationChangeStart = function(event, current, next) {
                
                if ($scope.ui_pristine) return;
                
                if (!$scope.search_location_ui_changed){    
                    
                    var qs = UtilsService.urlEncodeObject($location.search());
                        
                    $scope.search.setState($scope.search_default_state);
                    
                    $scope.search.setStateFromQueryString(qs, {
                        prefix: SearchConstants.ALGOLIA_PREFIX
                    });
                    
                    var other_params = algoliasearchHelper.url.getUnrecognizedParametersInQueryString(qs, {
                        prefixForParameters: SearchConstants.ALGOLIA_PREFIX
                    });
                    
                    $scope.search_location = other_params.location_name || "";
                    
                    $scope.search.search();
                } else {
                    $scope.search_location_ui_changed = false;
                }
            };
            
            
            $scope.refinePrices = function(sliderId){
                
                var state = $scope.search.getState();
                var newVal, oldVal;
                
                // TODO -1 and '>' are because $location.search() gets confused by '='. Fix this
                newVal = $scope.price_slider.min - 1;
                if (state.isNumericRefined("price", '>')){
                    oldVal = state.getNumericRefinement("price", '>')[0];
                    if (oldVal != newVal) {
                        $scope.search.removeNumericRefinement("price", '>');
                        $scope.search.addNumericRefinement("price", '>', newVal);
                    }
                } else {
                    $scope.search.addNumericRefinement("price", '>', newVal);
                }
                
                newVal = $scope.price_slider.max + 1;
                if (state.isNumericRefined("price", '<')){
                    oldVal = state.getNumericRefinement("price", '<')[0];
                    if (oldVal != newVal) {
                        $scope.search.removeNumericRefinement("price", '<');
                        $scope.search.addNumericRefinement("price", '<', newVal);
                    }
                } else {
                    $scope.search.addNumericRefinement("price", '<', newVal);
                }
                
                $scope.searchPage = 0;
                
                $scope.submitForm();
                
            };
                        
            $scope.refineRenterPart = function(newVal){
                var state = $scope.search.getState();
                if (newVal && !state.isDisjunctiveFacetRefined("pro_owner", false)){
                    $scope.search.addDisjunctiveFacetRefinement("pro_owner", false);
                }
                if (!newVal && state.isDisjunctiveFacetRefined("pro_owner", false)){
                    $scope.search.removeDisjunctiveFacetRefinement("pro_owner", false);
                    if (!$scope.owner_type.pro){
                        $scope.refineRenterPro(true);
                        return;
                    };
                }
                
                $scope.searchPage = 0;
                
                $scope.submitForm();
            };
            
            $scope.refineRenterPro = function(newVal){
                var state = $scope.search.getState();
                if (newVal && !state.isDisjunctiveFacetRefined("pro_owner", true)){
                    $scope.search.addDisjunctiveFacetRefinement("pro_owner", true);
                }
                if (!newVal && state.isDisjunctiveFacetRefined("pro_owner", true)){
                    $scope.search.removeDisjunctiveFacetRefinement("pro_owner", true);
                    if (!$scope.owner_type.part){
                        $scope.refineRenterPart(true);
                        return;
                    };
                }
                
                $scope.searchPage = 0;
                
                $scope.submitForm();
            };
            
            $scope.noProPartChoice = function(){
                return $scope.owner_type.pro_count==0 || $scope.owner_type.part_count==0;
            };
            
            $scope.refineCategory = function(path) {
                $scope.search.toggleRefinement("category", path);
                $scope.searchPage = 0;
                $scope.submitForm();
            };
            
            $scope.refineCategoryClearChildren = function(path) {
                $scope.search.toggleRefinement("category", path);
                $scope.search.toggleRefinement("category", path);
                $scope.searchPage = 0;
                $scope.submitForm();

            };
            $scope.refineBreadcrumbCategory = function(path) {
                $scope.search.toggleRefinement("category", path);
                $scope.search.toggleRefinement("category", path);
                $scope.search_query = '';
                $scope.searchPage = 0;
                $scope.refineLocation();
            };
            
            /*
             * Pagination & ordering 
             */
            
            $scope.nextPage = function(){
                $scope.setPage(Math.min($scope.page + 1, $scope.pages_count));
            };

            $scope.prevPage = function(){
                $scope.setPage(Math.max(1, $scope.page - 1));
            };
            
            $scope.setPage = function(page){
                $scope.searchPage = page-1;
                $scope.submitForm();
            };
            
            $scope.setOrdering = function(ordering){
                $scope.search
                    .setIndex(!!ordering ? $scope.search_index+"_"+ordering : $scope.search_index);
                $scope.searchPage = 0;
                $scope.submitForm();
            };
            
            $scope.resetMap = function(){};
            
            $scope.clearRefinements = function(){
                $scope.search.clearRefinements();
                var center = SearchConstants.COUNTRIES['fr'].center;
                var radius = SearchConstants.COUNTRIES['fr'].radius;
                $scope.search.setQueryParameter('aroundLatLng', center.latitude + ',' + center.longitude);
                $scope.search.setQueryParameter('aroundRadius', radius * 1000);
                $log.debug($scope.search.getState());
//                $scope.searchPage = 0;
                $scope.submitForm();
            };
            
            
            /* 
             * Filter rendering
             * */
            
            $scope.renderPagination = function(result){
                $scope.page = Math.min(result.nbPages, Math.max(1, result.page+1));
                var WINDOW_SIZE = SearchConstants.WINDOW_SIZE;
                if (result.nbPages < WINDOW_SIZE){
                    $scope.pages_range = new Array(result.nbPages);
                    for (var i=0; i<result.nbPages; i++){
                        $scope.pages_range[i] = i+1;
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
                        $scope.pages_range[i] = first+i+1;
                    }
                }
            };
            
            $scope.renderPriceSlider = function(result, state){
                
                var facetResult = result.getFacetByName("price");
                var ref;
                var statsMin = facetResult.stats.min, statsMax = facetResult.stats.max;
                
                $scope.price_slider.options.floor = $scope.price_slider.min = statsMin;
                if (state.isNumericRefined("price", '>')){
                    ref = state.getNumericRefinement("price", '>')[0] + 1;
                    $scope.price_slider.min = Math.max(statsMin, ref);
                }
                
                $scope.price_slider.options.ceil = $scope.price_slider.max = statsMax;
                if (state.isNumericRefined("price", '<')){
                    ref = state.getNumericRefinement("price", '<')[0] - 1;
                    $scope.price_slider.max = Math.min(statsMax, ref);
                }
                
            };

//            $scope.renderRangeSlider = function(result){                
//                $scope.map.zoom = UtilsService.zoom($scope.search.getQueryParameter('aroundRadius'));
//            };
            
            $scope.renderSearchCategories = function(result, state){
                if (result.hierarchicalFacets && result.hierarchicalFacets[0]) {
                    $scope.category = result.hierarchicalFacets[0];
                }
            };
                       
            $scope.renderBreadcrumbs = function(state) {
                if ("category" in state.hierarchicalFacetsRefinements){
                    $scope.search_breadcrumbs = [];
                    var cat = state.hierarchicalFacetsRefinements.category[0];
                    if (cat){
                        var catparts = cat.split(' > ');
                        $scope.leaf_category = catparts[catparts.length-1];
                        for (var i=0; i< catparts.length; i++){
                            $scope.search_breadcrumbs.push(
                                    {short: catparts[i], long: catparts.slice(0,i+1).join(' > ')});
                        }
                    } else {
                        $scope.leaf_category = "";
                    }
                }
            };
            
            $scope.renderRenterTypes = function(result, state){
                var facetResult = result.getFacetByName("pro_owner");
                $scope.owner_type.pro_count = ('true' in facetResult.data ? facetResult.data.true : 0);
                $scope.owner_type.part_count = ('false' in facetResult.data ? facetResult.data.false : 0);
                $scope.owner_type.pro = state.isDisjunctiveFacetRefined("pro_owner", true);
                $scope.owner_type.part = state.isDisjunctiveFacetRefined("pro_owner", false);
            };
            
            $scope.cooldown = false;
            $scope.searchDuringCooldown = false;
            $scope.cooldown_duration = 1000;
            
            $scope.get_query_string_options = function() {
                return {
                    filters: SearchConstants.URL_PARAMETERS, 
                    prefix: SearchConstants.ALGOLIA_PREFIX,
                    moreAttributes: {
                        location_name: $scope.search_location
                    }
                };
            };
            
            $scope.resetCooldown = function(){
                $scope.cooldown = false;
                if ($scope.searchDuringCooldown){
                    $scope.searchDuringCooldown = false;
                    $location.search(
                        $scope.search.getStateAsQueryString(
                            $scope.get_query_string_options()));
                }
            };
            
            $scope.renderLocation = function(result, state) {
                if ($scope.cooldown){
                    $scope.searchDuringCooldown = true;
                } else {
                    $scope.cooldown = true;
                    $location.search($scope.search.getStateAsQueryString(
                        $scope.get_query_string_options()));
                    $timeout($scope.resetCooldown, $scope.cooldown_duration);
                }
                
            };
            
            $scope.renderQueryText = function(result) {
                if (!$scope.search_location_ui_changed){
                    $scope.search_query = result.query;
                }
            };
            
            $scope.renderOrdering = function(result) {
                $scope.search_ordering = result.index.substr($scope.search_index.length+1);
            };
            
            /* 
             * Process search results 
             */
            
            $scope.processResult = function(result, state){
                
                $log.debug(result);
                
                $scope.search_result_count = result.nbHits;
                                                 
                $scope.product_list = result.hits;
                
                $scope.pages_count = result.nbPages;
                $scope.results_per_page = result.hitsPerPage;
                $scope.page = result.page;
                
                $scope.renderQueryText(result);
                $scope.renderOrdering(result);
                $scope.renderPagination(result);
                $scope.renderBreadcrumbs(state);
                $scope.renderMap(result, state);
            
                if ($scope.search_result_count){
                    $scope.renderLocation(result, state);
                    $scope.renderSearchCategories(result, state);
                    $scope.renderPriceSlider(result, state);
                    $scope.renderRenterTypes(result, state);
                } else {
                    $log.debug("No results");
                }
                
                $scope.ui_pristine = false;
                $scope.$apply();
                
            };
            
            $scope.processError = function(error){
                $log.error(error);
            };
            
            $scope.search.on('result', $scope.processResult)
                .on('error', $scope.processError);
            
            
            $scope.resetQuery = function(){
                $scope.search_query = "";
            };
            
            $scope.resetFilters = function(){
                
            };
            
            
            var orig_params = $location.search();
            
            $scope.search_location_ui_changed = false;
            $scope.search_query = UtilsService.getParameterByName('q') || "";
            $scope.search.setQuery($scope.search_query);
            $scope.search_location = UtilsService.getParameterByName('l') || "";
            $scope.product_list = [];
            $scope.searchPage = 0;
            $scope.search_result_count = 0;
            $scope.product_list_price_max = 1000;
            $scope.product_list_price_min = 0;
            $scope.price_from = 0;
            $scope.price_to = 1000;
            $scope.owner_type = {
                pro: true,
                part: true,
                pro_count: 0,
                part_count: 0
            };
            $scope.search_breadcrumbs = [];
            $scope.search_location = UtilsService.getParameterByName('l') || "";
            $scope.search_bounds_changed = false;
            $scope.boundsChangedByRender = false;
            $scope.ui_pristine = true;
            $scope.price_slider = {
                min: 0,
                max: 1000,
                options: {
                    floor: 0,
                    ceil: 1000,
                    onEnd: $scope.refinePrices
                }
            };
            $scope.range_slider = {
                max: $scope.search_max_range,
                options: {
                    floor: 1,
                    ceil: $scope.search_max_range,
                    onEnd: $scope.refineRange
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
            
            $scope.submitForm = function() {
                // TODO remove from here
                if ($scope.ui_pristine) {
                    $scope.$on("$locationChangeStart", $scope.onLocationChangeStart);
                } 
                $scope.search_location_ui_changed = true;
                $scope.search.setQuery($scope.search_query)
                    .setCurrentPage($scope.searchPage).search();
            };

            $scope.newSearch = function(){
                $scope.searchPage = 0;
                $scope.submitForm();                
            };
            
            $scope.disableForm = function() {
                setTimeout(function() {
                    $("input, select").attr("disabled", true);
                    $(".jslider-pointer").attr("style", "display: none !important");
                    $("#submitButton").addClass("loading");
                }, 50);

            };

            $scope.activateLayoutSwitcher();
            
        }]);
});
