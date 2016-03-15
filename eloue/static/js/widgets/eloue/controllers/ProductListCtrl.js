define([
    "eloue/app",
    "../../../common/eloue/services/UtilsService",
    "algoliasearch-helper",
    "stacktrace",
    "js-cookie"
], function (EloueWidgetsApp, UtilsService, algoliasearchHelper, StackTrace, Cookies) {
    "use strict";
    
    var Point = function(lat, lng){
        return {
            type:"Point",
            coordinates:[lng, lat]
        };
    };
    
    function gmapToGeoJson(point){
        return {
            type:"Point",
            coordinates:[point.lng(), point.lat()]
        };
    };
    
    function algoliaToGeoJson(point){
        var arr = point.split(',');
        return {
            type:"Point",
            coordinates:[parseFloat(arr[1]), parseFloat(arr[0])]
        };
    };
    
    function geoJsonToAlgolia(point){
        return point.coordinates[1]+','+point.coordinates[0];
    };
        
    var el = Cookies.get("eloue_el");
    
    function hasStorage(){
        return typeof(Storage) !== 'undefined';
    };
    
    function cleanup(){
        if (hasStorage()){
            var i = sessionStorage.length;
            while (i--){
                var key = sessionStorage.key(i);
                if (key.match(/^eloue_err_.*/g)){
                    sessionStorage.removeItem(key);
                }
            }
        } 
    };
    
    if (el){
        EloueWidgetsApp.factory('$exceptionHandler', function() {
            
            function frameKey(f) {
                return f.functionName+'@'+f.fileName+':'+f.lineNumber+':'+f.columnNumber;
            };
            
            var ec = parseInt(Cookies.get('eloue_ec')) || 0;
            
            if (!ec){
                cleanup();
            }
            
            var log;
            
            if (hasStorage()){
                log = function(trace){
                    var topFrame = trace[0];
                    var key = 'eloue_err_'+frameKey(topFrame);
                    var exceptionCount = parseInt(Cookies.get('eloue_ec')) || 0;
                    if (exceptionCount<parseInt(el) && !(sessionStorage.getItem(key))){
                        Cookies.set('eloue_ec', exceptionCount+1);
                        sessionStorage.setItem(key,1);
                        StackTrace.report(trace, "/logs/").then(function(resp){
                        }).catch(function(resp){
                        });
                    };
                };
            } else {
                log = function(trace){
                    var topFrame = trace[0];
                    var key = 'eloue_err_'+frameKey(topFrame);
                    var exceptionCount = Cookies.get('eloue_ec');
                    if (!exceptionCount){
                        Cookies.set('eloue_ec', 1);
                        StackTrace.report(trace, "/logs/").then(function(resp){
                        }).catch(function(resp){
                        });
                    };
                };
            }
            
            return function(exception, cause) {                
                StackTrace.fromError(exception, {offline:false})
                    .then(log).catch(function(trace){});
            };
        });    
    } else {
        cleanup();
    }

    EloueWidgetsApp.filter('safe', [
      '$sce',
      function($sce) {
        return function(text, type) {
          return $sce.trustAs(type || 'html', text);
        }
      }
    ]);
    
    EloueWidgetsApp.filter('title', [
    function() {
        return function(text) {
            if (text) {
                var words = text.split(" ");
                for (var i=0; i<words.length; i++){
                    words[i] = words[i].charAt(0).toUpperCase() + words[i].slice(1).toLowerCase();
                }
                return words.join(" ");    
            } else {
                return "";
            }
        }
    }]);
                                  
    
    EloueWidgetsApp.config(['uiGmapGoogleMapApiProvider', function(uiGmapGoogleMapApiProvider) {
        uiGmapGoogleMapApiProvider.configure({
            v: '3.exp',
            libraries: ['places', 'geometry'],
            language: 'fr-FR',
            region: 'FR'
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
                sortBy: ['name:asc']
            }],
            disjunctiveFacets: ["pro_owner",
                                "price",
                                "sites"],
            facets: ["is_archived", 
                     'is_good'],
            hitsPerPage: 12,
            aroundLatLng:"46.2,2.2",
            aroundRadius:1000000,
            query:""
        },
        ALGOLIA_PREFIX: "sp_",
        ALGOLIA_APP_ID: 'NSV6X2HQLR',
        ALGOLIA_KEY:'1f470a5fbfd05ca06ac97a01bca6a4eb',
        URL_PARAMETERS: ['query', 'attribute:*', 'index', 'page', 
                         'hitsPerPage', 'aroundLatLng', 'aroundRadius'],
        URL_PARAMETERS_EXCLUDE: ['is_archved', 
                                 'is_good', 
                                 'sites'],
        DEFAULT_ORDERING: "",
        WINDOW_SIZE: 10,
        COUNTRIES: {
          'fr': {
            center: Point(46.2, 2.2),
            radius: 1000,
            location_name: "France"
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
        "$filter",
        "$q",
        "$log",
        "UtilsService",
        "SearchConstants",
        "uiGmapGoogleMapApi",
        "uiGmapIsReady",
        "algolia",
        function ($scope, $window, $timeout, $document, $location, $filter, $q, $log, 
                UtilsService, SearchConstants, uiGmapGoogleMapApi, uiGmapIsReady, algolia) {
            
            $scope.search_max_range = 1000;
            $scope.country = 'fr';
            
//            $scope.search_ordering = SearchConstants.DEFAULT_ORDERING;
            $scope.search_index = SearchConstants.MASTER_INDEX;
            
            $scope.get_index = function(){
                return !!$scope.search_ordering ? 
                        $scope.search_index+"_"+$scope.search_ordering : $scope.search_index;
            };
            
            function algoliaCoords(point){
                return point.latitude + ',' + point.longitude;
            };
            
            function angularGmapCords(point){
                
                return {latitude:parseFloat(arr[0]), longitude:parseFloat(arr[1])};
            };

            
            /* 
             * Algolia config 
             */
            var client = algolia.Client(SearchConstants.ALGOLIA_APP_ID, SearchConstants.ALGOLIA_KEY);
            $scope.search = algoliasearchHelper(client, $scope.get_index(), SearchConstants.PARAMETERS);
            $scope.search.addDisjunctiveFacetRefinement("pro_owner", true);
            $scope.search.addDisjunctiveFacetRefinement("pro_owner", false);
            $scope.search.addDisjunctiveFacetRefinement("sites", 1);
            $scope.search.addFacetRefinement("is_archived", false);
            $scope.search_default_state = $scope.search.getState();
            
            /*
             * Map config
             */

            var staticUrl = "/static/", scripts = $document[0].getElementsByTagName("script"), i, j, l,
                        product, image, imageHover, myLatLng, marker;
                    for (i = 0, l = scripts.length; i < l; i += 1) {
                        if (scripts[i].getAttribute("data-static-path")) {
                            staticUrl = scripts[i].getAttribute("data-static-path");
                            break;
                        }
                    }

            $scope.map = {
                loaded: false,
                zoom: UtilsService.zoom(SearchConstants.COUNTRIES[$scope.country].radius),
                center: SearchConstants.COUNTRIES[$scope.country].center,
                options:{
                    disableDefaultUI: true,
                    zoomControl: true,
                    maxZoom: 14
                },
                clustererOptions:{
                    maxZoom:13,
                    styles:[
                        {
                            textColor: 'white',
                            textSize: 14,
                            url: staticUrl + 'img/markerclustericon.png',
                            height: 43,
                            width: 43,
                        },
                    ]
                },
                control: {}
            };
            
            $scope.refineRange = function(sliderid){ //$log.debug('refineRange');
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
            
            $scope.search_location_geocoded_deferred = $q.defer();
            $scope.search_location_geocoded_promise = $scope.search_location_geocoded_deferred.promise;
            
            // On map loaded
            $scope.mapLoadedPromise = uiGmapGoogleMapApi.then(function(maps) {

                var placeInputHead = $document[0].getElementById('geolocate');
                var geoc = new maps.Geocoder();

                var ac_params = {
                    componentRestrictions: {country: 'fr'}
                };
                
                var autocomplete_head = new maps.places.Autocomplete(placeInputHead,ac_params);
                
                $scope.setLatLongRadiusFromPlace = function(place){
                    $scope.search_location = place.formatted_address;
                    if ("viewport" in place.geometry){
                        $scope.range_slider.max = Math.ceil(maps.geometry.spherical.computeDistanceBetween(
                                place.geometry.viewport.getNorthEast(),
                                place.geometry.viewport.getSouthWest())/2000);
                    } 
                    $scope.search_center = gmapToGeoJson(place.geometry.location);
                };
                
                $scope.refineLocationByPlace = function(place){ //$log.debug('refineLocationByPlace');
                    $scope.setLatLongRadiusFromPlace(place);
                    $scope.search_ordering = "distance";
                    $scope.setOrdering();
                };
                
                uiGmapIsReady.promise(1).then(function(instances) {
                    instances.forEach(function(inst) {
                        var map = inst.map;
                       
                        $scope.map.options.mapTypeId = maps.MapTypeId.ROADMAP;
                        
                        var autocompleteChangeListener = function(autocomplete) {

                            return function(){
                                
                                $scope.$apply(function(){

                                    var place = autocomplete.getPlace();
                                    
                                    if (!('location' in place.geometry)){
                                        
                                        geoc.geocode({address:place.formatted_address}, function(results, status){
                                            $scope.$apply(function(){
                                                if (status==maps.GeocoderStatus.OK){
                                                    //$log.debug(results);
                                                    place.geometry = results[0].geometry;
                                                    $scope.refineLocationByPlace(place);
                                                } else {
                                                    //$log.debug("GEOCODER ERROR: "+status);
                                                    //TODO handle geocoding error
                                                }
                                            });
                                        });
                                    } else {
                                        $scope.refineLocationByPlace(place);
                                    }
                                });
                                
                            };
                        };
                        autocomplete_head.addListener('place_changed', autocompleteChangeListener(autocomplete_head));
                        
                    });
                    
                    
                });
                
                $scope.get_marker_images = function(){ //$log.debug('get_marker_images');
                    
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
                
                $scope.renderMap = function(result, state) { //$log.debug('renderMap');
                    
                    $scope.map.boundsChangedByRender = true;
                    
                    //$log.debug('== renderMap ==');
                    
                    for (var ri=0; ri<$scope.product_list.length; ri++){
                        var res = $scope.product_list[ri];
                        res.location_obj = Point(res.locations[0], res.locations[1]);
                        res.images = $scope.marker_images[ri];
                        res.markerId = ri;
                        res.markerOptions = {
                            icon: res.images.normal,
                            title: res.plain_summary,
                            zIndex: ri
                        };
                    };
                    var gmap = $scope.map.control.getGMap();
                    
                    //$log.debug(state.getQueryParameter('aroundLatLng'));
                    //$log.debug(state.getQueryParameter('aroundRadius'));
                    
                    //$log.debug("map center: "); 
                    //$log.debug(algoliaToGeoJson(state.getQueryParameter('aroundLatLng')));
                    $scope.map.center = algoliaToGeoJson(state.getQueryParameter('aroundLatLng'));
                    var radius = parseFloat(state.getQueryParameter('aroundRadius'))/1000;
                    $scope.map.zoom = UtilsService.zoom(radius);
                    
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
                
//                $scope.triggerMouseOverGenerator = function (marker) { //$log.debug('triggerMouseOverGenerator');
//                    return function () {
//                        marker.setAnimation(google.maps.Animation.BOUNCE);
//                        google.maps.event.trigger(marker, "mouseover");
//                    };
//                };
//
//                $scope.triggerMouseOutGenerator = function (marker) { //$log.debug('triggerMouseOutGenerator');
//                    return function () {
//                        marker.setAnimation(null);
//                        google.maps.event.trigger(marker, "mouseout");
//                    };
//                };
                
                if ($scope.search_location) {
                    geoc.geocode({address:$scope.search_location}, function(results, status){
                        $scope.$apply(function(){
                            if (status==maps.GeocoderStatus.OK){
                                //$log.debug("geocoded");
                                $scope.search_ordering = 'distance';
                                $scope.search_center = gmapToGeoJson(results[0].geometry.location);
                                $scope.search_location_geocoded_deferred.resolve(results, status);
                            } else {
                                //$log.debug("GEOCODER ERROR: "+status);
                                $scope.search_location_geocoded_deferred.reject(results, status);
                            }
                        });
                    });
                } else {
                    $scope.search_location_geocoded_deferred.resolve();
                }
                
                $scope.map.loaded = true;

            });
            
            /* 
             * Filter refinement 
             */
            
            $scope.onLocationChangeStart = function(event, current, next) { //$log.debug('onLocationChangeStart');
                
//                if (!$scope.orig_params_present()) return;
                
                if (!$scope.search_location_ui_changed){    
                    
                    var qs = UtilsService.urlEncodeObject($location.search());
                        
                    $scope.search.setState($scope.search_default_state);
                   
                    if ($scope.ui_pristine) {
                        $scope.search_location_geocoded_promise.finally($scope.submitForm);
                        return;
                    }
                    
                    $scope.search.setStateFromQueryString(qs, {
                        prefix: SearchConstants.ALGOLIA_PREFIX
                    });
                    
                    var other_params = algoliasearchHelper.url.getUnrecognizedParametersInQueryString(qs, {
                        prefixForParameters: SearchConstants.ALGOLIA_PREFIX
                    });
                    
                    $scope.search_location = other_params.location_name || "";
                    
                    //$log.debug($scope.search.getState());
                    
                    $scope.search.search();
                } else {
                    $scope.search_location_ui_changed = false;
                }
            };
            
            
            $scope.refinePrices = function(sliderId){ //$log.debug('refinePrices');
                
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
                        
            $scope.refineRenterPart = function(newVal){ //$log.debug('refineRenterPart');
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
            
            $scope.refineRenterPro = function(newVal){ //$log.debug('refineRenterPro');
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
            
            $scope.noProPartChoice = function(){ //$log.debug('noProPartChoice');
                return $scope.owner_type.pro_count==0 || $scope.owner_type.part_count==0;
            };
            
            $scope.refineCategory = function(path) { //$log.debug('refineCategory');
                $scope.search_category_path = path;
                $scope.search.toggleRefinement("category", $scope.search_category_path);
                $scope.searchPage = 0;
                $scope.submitForm();
            };
            
            $scope.refineCategoryClearChildren = function(path) { //$log.debug('refineCategoryClearChildren');
                $scope.search.toggleRefinement("category", path);
                $scope.search.toggleRefinement("category", path);
                $scope.searchPage = 0;
                $scope.submitForm();

            };
            $scope.refineBreadcrumbCategory = function(path) { //$log.debug('refineBreadcrumbCategory');
                $scope.search.toggleRefinement("category", path);
                $scope.search.toggleRefinement("category", path);
                $scope.search_query = '';
                $scope.searchPage = 0;
                $scope.refineLocation();
            };
            
            /*
             * Pagination & ordering 
             */
            
            $scope.nextPage = function(){ //$log.debug('nextPage');
                $scope.setPage(Math.min($scope.page + 1, $scope.pages_count));
            };

            $scope.prevPage = function(){ //$log.debug('prevPage');
                $scope.setPage(Math.max(1, $scope.page - 1));
            };
            
            $scope.setPage = function(page, callId){ //$log.debug('setPage '+page+' '+callId);
                $scope.searchPage = page-1;
                $scope.submitForm();
            };
            
            $scope.setOrdering = function(ordering){ //$log.debug('setOrdering');
//                $scope.search
//                    .setIndex($scope.get_index());
//                $scope.search_ordering = ordering;
                $scope.searchPage = 0;
                $scope.submitForm();
            };
            
            $scope.resetMap = function(){};
            
            $scope.clearRefinements = function(){ //$log.debug('clearRefinements');
                $scope.search.setState($scope.search_default_state);
                //$log.debug($scope.search.getState());
//                $scope.search_query = "";
                $scope.search_location = "";
                $scope.search.search();
            };
            
            
            /* 
             * Filter rendering
             * */
            
            $scope.renderPagination = function(result){ //$log.debug('renderPagination');
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
            
            $scope.renderPriceSlider = function(result, state){ //$log.debug('renderPriceSlider');
                
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

            $scope.renderRangeSlider = function(result, state){ //$log.debug('renderRangeSlider');          
            
                var radius = state.aroundRadius/1000 || UtilsService.zoom(SearchConstants.COUNTRIES[$scope.country].radius);
                $scope.range_slider.max = radius;
            };
            
            $scope.renderSearchCategories = function(result, state){ //$log.debug('renderSearchCategories');
                if (result.hierarchicalFacets && result.hierarchicalFacets[0]) {
                    $scope.category = result.hierarchicalFacets[0];
                }
            };
                       
            $scope.renderBreadcrumbs = function(state) { //$log.debug('renderBreadcrumbs');
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
            
            $scope.renderRenterTypes = function(result, state){ //$log.debug('renderRenterTypes');
                var facetResult = result.getFacetByName("pro_owner");
                $scope.owner_type.pro_count = ('true' in facetResult.data ? facetResult.data.true : 0);
                $scope.owner_type.part_count = ('false' in facetResult.data ? facetResult.data.false : 0);
                $scope.owner_type.pro = state.isDisjunctiveFacetRefined("pro_owner", true);
                $scope.owner_type.part = state.isDisjunctiveFacetRefined("pro_owner", false);
            };
            
            $scope.cooldown = false;
            $scope.searchDuringCooldown = false;
            $scope.cooldown_duration = 1000;
            
            $scope.get_query_string_options = function() { //$log.debug('get_query_string_options');
                return {
                    filters: SearchConstants.URL_PARAMETERS, 
                    prefix: SearchConstants.ALGOLIA_PREFIX,
                    moreAttributes: {
                        location_name: $scope.search_location
                    }
                };
            };
            
            $scope.resetCooldown = function(){ //$log.debug('resetCooldown');
                $scope.cooldown = false;
                if ($scope.searchDuringCooldown){
                    $scope.searchDuringCooldown = false;
                    $location.search(
                        $scope.search.getStateAsQueryString(
                            $scope.get_query_string_options()));
                }
            };
            
            $scope.renderLocation = function(result, state) { //$log.debug('renderLocation');
                if ($scope.ui_pristine){
                    $location.replace();
                }
                if ($scope.cooldown){
                    $scope.searchDuringCooldown = true;
                } else {
                    $scope.cooldown = true;
                    $location.search($scope.search.getStateAsQueryString(
                        $scope.get_query_string_options()));
                    $timeout($scope.resetCooldown, $scope.cooldown_duration);
                }
            };
            
            $scope.renderQueryText = function(result) { //$log.debug('renderQueryText');
                //$log.debug('search_location_ui_changed='+$scope.search_location_ui_changed);
                if (!$scope.search_location_ui_changed){
                    $scope.search_query = result.query;
                }
            };
            
            $scope.renderOrdering = function(result) { //$log.debug('renderOrdering');
                $scope.search_ordering = result.index.substr($scope.search_index.length+1);
            };
            
            /* 
             * Process search results 
             */
            
            $scope.processResult = function(result, state){ //$log.debug('processResult');
                
                $scope.$apply(function(){
                    //$log.debug(result.page);
                    //$log.debug(result);
                    
                    $scope.search_result_count = result.nbHits;
                    $scope.product_list = result.hits;
                    
                    for (var ri=0; ri<$scope.product_list.length; ri++){
                        var res = $scope.product_list[ri];
                        for (var k in res['_highlightResult']){
                            res["plain_"+k] = res[k];
                            res[k] = res['_highlightResult'][k]['value'];
                        }
                    }
                    
                    $scope.results_per_page = result.hitsPerPage;
                    
                    if ($scope.search_result_count){
                        $scope.page = result.page;
                        $scope.pages_count = result.nbPages;
                        $scope.renderPagination(result);
                        $scope.renderSearchCategories(result, state);
                        $scope.renderPriceSlider(result, state);
                        $scope.renderRenterTypes(result, state);
                    } else {
                        //$log.debug("No results");
                    }
                    
                    $scope.renderQueryText(result);
                    $scope.renderOrdering(result);
                    $scope.renderBreadcrumbs(state);
                    $scope.renderRangeSlider(result, state);
                    if ($scope.map.loaded){
                        $scope.renderMap(result, state);
                    } else {
                        $scope.mapLoadedPromise.then(function(){
                            $scope.renderMap(result, state);
                        });
                    }
                    $scope.renderLocation(result, state);
                    
                    //$log.debug($scope.product_list);
                    
                    $scope.ui_pristine = false;
                    
                    $scope.request_pending = false;
                    
                });
                
            };
            
            $scope.processError = function(error){ //$log.debug('processError');
                
                $scope.$apply(function(){
                    $scope.request_pending = false;
                });
            };
            
            $scope.search.on('result', $scope.processResult)
                .on('error', $scope.processError);
            
            $scope.resetQuery = function(){ //$log.debug('resetQuery');
                $scope.search_query = "";
            };
            
            $scope.orig_params = $location.search();
            
            //$log.debug($scope.orig_params);
            $scope.orig_params_present = function(){
                var orig_params = $location.search();
                return !!orig_params && Object.keys(orig_params).length > 0;
            }
            //$log.debug('orig_params_present='+$scope.orig_params_present());
            
            $scope.search_location_ui_changed = false;
            $scope.search_query = UtilsService.getParameterByName('q') || "";
            $scope.search_location = UtilsService.getParameterByName('l') || "";
            $scope.search_center = SearchConstants.COUNTRIES['fr'].center;
            $scope.product_list = [];
            $scope.searchPage = 0;
            $scope.search_result_count = 0;
            $scope.product_list_price_max = 1000;
            $scope.product_list_price_min = 0;
            $scope.search_category_path = "";
            $scope.price_from = 0;
            $scope.price_to = 1000;
            $scope.owner_type = {
                pro: true,
                part: true,
                pro_count: 0,
                part_count: 0
            };
            $scope.search_breadcrumbs = [];
            $scope.search_bounds_changed = false;
            $scope.map.boundsChangedByRender = false;
            $scope.ui_pristine = !$scope.orig_params_present();
            $scope.price_slider = {
                min: 0,
                max: 1000,
                options: {
                    floor: 0,
                    ceil: 1000,
                    onEnd: $scope.refinePrices,
                    translate: function(value) {
                        return value + " €";
                    }
                }
            };
            $scope.range_slider = {
                max: $scope.search_max_range,
                options: {
                    floor: 1,
                    ceil: $scope.search_max_range,
                    onEnd: $scope.refineRange,
                    translate: function(value) {
                        return value + " km";
                    }
                }    
            };            

            $scope.activateLayoutSwitcher = function () { //$log.debug('activateLayoutSwitcher');
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
            
            if ($scope.orig_params_present()) {
                $scope.map_callbacks = false;
            } 

            $scope.$on("$locationChangeStart", $scope.onLocationChangeStart);
            
            $scope.submitForm = function() { //$log.debug('submitForm');
                if ($scope.request_pending) {
                    return;
                }
                $scope.request_pending = true;
                // TODO remove from here
                if ($scope.ui_pristine && !$scope.orig_params_present()) {
//                    $scope.$on("$locationChangeStart", $scope.onLocationChangeStart);
                    $scope.orig_params = null;
                } 
                $scope.search_location_ui_changed = true;
                
                if ($scope.ui_pristine){
                    $scope.search.toggleRefinement("category", $scope.search_category_path);
                }
                
                $scope.search.setQuery($scope.search_query)
                    .setQueryParameter('aroundLatLng', geoJsonToAlgolia($scope.search_center))
                    .setQueryParameter('aroundRadius', $scope.range_slider.max * 1000)
                    .setCurrentPage($scope.searchPage)
                    .setIndex($scope.get_index())
                    .search();
            };

            $scope.newSearch = function(){ //$log.debug('newSearch');
                $scope.searchPage = 0;
                $scope.submitForm();                
            };
            
            $scope.disableForm = function() { //$log.debug('disableForm');
                setTimeout(function() {
                    $("input, select").attr("disabled", true);
                    $(".jslider-pointer").attr("style", "display: none !important");
                    $("#submitButton").addClass("loading");
                }, 50);

            };

            $scope.activateLayoutSwitcher();
            
        }]);
});
