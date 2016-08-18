define([
    "eloue/app",
    "../../../common/eloue/services/UtilsService",
    "../../../common/eloue/services/CategoriesService",
    "algoliasearch-helper",
    "stacktrace",
    "js-cookie",
    "../i18n"
], function (EloueWidgetsApp, UtilsService, CategoriesService, algoliasearchHelper, StackTrace, Cookies) {
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
                return text.replace(/(?:<em>)?([^\s]+)/g, function(txt, gr1){
                    return txt.replace(gr1, gr1.charAt(0).toUpperCase() 
                            + gr1.slice(1).toLowerCase());});
            } else {
                return "";
            }
        }
    }]);
                
    EloueWidgetsApp.filter('is_facet', [
    function() {
        return function(props) {
            var res = [];
            if (props) {
                for (var i=0; i<props.length; i++){
                    if (props[i].faceted){
                        res.push(props[i]);   
                    }
                }
            } 
            return res;
        }
    }]);
                                     
    
    EloueWidgetsApp.config(['uiGmapGoogleMapApiProvider', 'MAP_CONFIG', function(uiGmapGoogleMapApiProvider, MAP_COFNIG) {
        
        // TODO a hack to get the language 
        var lang = angular.element(document)[0].documentElement.lang;
        
        var conf = $.extend({
            v: '3.exp',
            libraries: ['places', 'geometry'],
        }, MAP_COFNIG[lang]);
        
        uiGmapGoogleMapApiProvider.configure(conf);

    }]);
   
   
   EloueWidgetsApp.directive('elouePropertyDropdownFilter', function(){
        return {
            template: '<label class="caption", for="{{proto.attr_name+proto.id}}">{{proto.name}}</label>'+
                    '<select id="{{proto.attr_name+proto.id}}" ng-model="value" '+
                      'ng-options="choice for choice in proto.choices" '+
                      'data-placeholder="{{proto.name}}" '+
                      'class="form-control" eloue-chosen></select>',
            restrict: 'A',
            require: 'ngModel', 
            scope: {
                proto: '=propertyType'
            },
            link: function (scope, element, attrs, ngModel) {
                
                ngModel.$render = function(){
                    scope.value = ngModel.$viewValue;
                };
                
                scope.$watch('value', function(newVal, oldVal, scope){
                    ngModel.$setViewValue(newVal);
                });
              
          }
        };
    });
    
    
    EloueWidgetsApp.directive('eloueSliderFilter', ['$filter', '$log', function($filter, $log){
        return {
            template:
                '<div ng-if="ready()">'+   
                    '<label class="caption" '+
                        'for="{{label}}-slider">{{label}}</label>'+
                    '<rzslider ng-if="!is_range()" id="{{label}}-slider" '+
                        'ng-model="value.max", rz-slider-model="value.max" '+
                        'rz-slider-options="value.options"/>'+
                    '<rzslider ng-if="is_range()" id="{{label}}-slider" '+
                        'rz-slider-model="value.min" rz-slider-high="value.max" '+
                        'ng-model="value.min" rz-slider-options="value.options"/>'+
                '</div>',
            restrict: 'E',
            require: 'ngModel',
            scope: {
                proto: '=propertyType',
                label: '@',
                i18n: '@'
            },
            link: function (scope, element, attrs, ngModel) {
                
                var onEnd;
                
                function toMetric(val, k){
                    return Math.round(val*k);
                } 
                
                function fromMetric(val, k){
                    return Math.round(val/k);
                } 
                
                function translate(value){
                    return $filter("translate")(scope.i18n, {value:value});
                }
                
                scope.is_range = function(){
                    return 'min' in scope.value;
                };
                
                scope.ready = function(){
                    return 'max' in scope.value && 
                        'ceil' in scope.value.options && 
                        'floor' in scope.value.options;
                };
                
                ngModel.$formatters.push(function(val){//$log.debug('format');
                    var value = $.extend(true, {}, val);
                    var k = value.from_metric;
                    if (k){
                        value.options.ceil = fromMetric(value.options.ceil, k);
                        value.options.floor = fromMetric(value.options.floor, k);
                        value.max = fromMetric(value.max, k);
                        if (scope.is_range()){
                            value.min = fromMetric(value.min, k);   
                        }   
                    }
                    // $log.debug(value);
                    return value;
                });
                
                ngModel.$parsers.push(function(val){//$log.debug('parse');
                    var value = $.extend(true, {}, val);
                    var k = value.to_metric;
                    if (k){
                        value.options.ceil = toMetric(value.options.ceil);
                        value.options.floor = toMetric(value.options.floor);
                        value.max = toMetric(value.max);
                        if (scope.is_range()){
                            value.min = toMetric(value.min);   
                        }   
                    }
                    // $log.debug(value);
                    return value;
                });
                
                onEnd = function (){//$log.debug('onEnd');
                        
                    // Create a new object to trigger ng-model change
                    var val = {
                        max: scope.value.max,
                        options:{
                            ceil: scope.value.options.ceil,
                            floor: scope.value.options.floor
                        }
                    };
                    if (scope.is_range()){
                        val.min = scope.value.min;   
                    }
                    // $log.debug(val);
                    ngModel.$setViewValue(val);
                    
                };
                
                ngModel.$render = function(){ //$log.debug('render');
                    scope.value = $.extend(true, scope.value, ngModel.$viewValue);
                    // $log.debug(scope.value);
                };
                
                scope.value = {
                    options:{
                        translate: translate,
                        onEnd: onEnd
                    }
                };
                
          }
        };
    }]);
    
   
    
    /**
     * Controller to run scripts necessary for product list page.
     */
    EloueWidgetsApp.controller("AlgoliaProductListCtrl", [
        "$scope",
        "$window",
        "$timeout",
        "$document",
        "$location",
        "$filter",
        "$q",
        "$log",
        "UtilsService",
        "CategoriesService",
        "uiGmapGoogleMapApi",
        "uiGmapIsReady",
        "algolia",
        function ($scope, $window, $timeout, $document, $location, $filter, $q, $log, 
                UtilsService, CategoriesService, uiGmapGoogleMapApi, uiGmapIsReady, algolia) {
            
            var unsubscribe = $scope.$watch('search_params', function(search_params){

                
                unsubscribe();
                
                $scope.search = $.extend(true, {}, search_params.defaults, search_params.init);
                

//                $log.debug('Initial parameters:');
//                $log.debug($scope.search);
                
                $scope.search.index = search_params.config.MASTER_INDEX;
                $scope.search.pages_count = Math.ceil($scope.search.result_count/search_params.config.PARAMETERS.hitsPerPage);

                $scope.get_index = function(){
                    return !!$scope.search.order_by ? 
                            $scope.search.index+"_"+$scope.search.order_by : $scope.search.index;
                };
                
                $scope.makePaginationModel = function(nbPages, page){
                    $scope.search.page = Math.min(nbPages-1, Math.max(0, page));
                    var PAGINATION_WINDOW_SIZE = search_params.config.PAGINATION_WINDOW_SIZE;
                    if (nbPages < PAGINATION_WINDOW_SIZE){
                        $scope.search.pages_range = new Array(nbPages);
                        for (var i=0; i<nbPages; i++){
                            $scope.search.pages_range[i] = i;
                        }
                    } else {
                        if ($scope.search.page > nbPages/2){
                            var last = Math.min(page+Math.ceil(PAGINATION_WINDOW_SIZE/2+1), nbPages-1);    
                            var first = Math.max(0, last-PAGINATION_WINDOW_SIZE);
                        } else {
                            var first = Math.max(0, page-Math.floor(PAGINATION_WINDOW_SIZE/2+1));
                        }
                        $scope.search.pages_range = new Array(PAGINATION_WINDOW_SIZE);
                        for (var i=0; i<PAGINATION_WINDOW_SIZE; i++){
                            $scope.search.pages_range[i] = first+i;
                        }
                    }
                };
                
                $scope.makePaginationModel($scope.search.pages_count, $scope.search.page);
                
                /* 
                 * Algolia config 
                 */
                var client = algolia.Client(search_params.config.ALGOLIA_APP_ID, search_params.config.ALGOLIA_KEY);
                $scope.search.helper = algoliasearchHelper(client, $scope.get_index(), search_params.config.PARAMETERS);
                $scope.search.helper.addDisjunctiveFacetRefinement("pro_owner", true);
                $scope.search.helper.addDisjunctiveFacetRefinement("pro_owner", false);
                $scope.search.helper.addDisjunctiveFacetRefinement("sites", $scope.search.site);
                $scope.search.helper.addFacetRefinement("is_archived", false);
                $scope.search.helper.addFacetRefinement("is_allowed", true);
                $scope.search.helper.setQueryParameter('aroundRadius', search_params.defaults.range.max * 1000);
                $scope.search.helper.setQueryParameter('aroundLatLng', search_params.defaults.center[0]+
                        ','+search_params.defaults.center[1]);
                $scope.search_default_state = $scope.search.helper.getState();
                
//                $log.debug($scope.search_default_state);
                
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

                $scope.search.map = {
                    loaded: false,
                    zoom: UtilsService.zoom($scope.search.center),
                    center: Point($scope.search.center[0],$scope.search.center[1]),
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
                    $scope.search.helper.setQueryParameter('aroundRadius', $scope.search.range.max * 1000);
                    $scope.perform_search();
                };
                
                $scope.rangeUpdatedBySlider = false;
                
                $scope.search.location_geocoded_deferred = $q.defer();
                $scope.search.location_geocoded_promise = $scope.search.location_geocoded_deferred.promise;
                
                $scope.setOrderByDistance = function(){
                    if ($scope.search.location !== search_params.defaults.location){
                        $scope.search.order_by = "distance";
                    }
                };
                
                
                // On map loaded
                $scope.search.mapLoadedPromise = uiGmapGoogleMapApi.then(function(maps) {

                    var placeInputHead = $document[0].getElementById('geolocate');
                    var geoc = new maps.Geocoder();

                    var ac_params = {
                        //componentRestrictions: {country: 'fr'}
                    };
                    
                    var autocomplete_head = new maps.places.Autocomplete(placeInputHead,ac_params);
                    
                    $scope.setLatLongRadiusFromPlace = function(place){
                        if (!place){
                            $scope.search.location = $scope.search.location_geocoded = search_params.defaults.location;
                            $scope.search.range.max = search_params.defaults.range.max;
                            $scope.search.center = Point($scope.search.center[0],$scope.search.center[1]);
                            return;
                        }
                        $scope.search.location = $scope.search.location_geocoded = place.formatted_address;
                        if ("viewport" in place.geometry){
                            $scope.search.range.max = Math.ceil(maps.geometry.spherical.computeDistanceBetween(
                                    place.geometry.viewport.getNorthEast(),
                                    place.geometry.viewport.getSouthWest())/2000);
                        } 
                        $scope.search.center = gmapToGeoJson(place.geometry.location);
                    };
                    
                    $scope.refineLocation = function(place){ //$log.debug('refineLocation');
                        $scope.setLatLongRadiusFromPlace(place);
                        $scope.setOrderByDistance();
                        $scope.setOrdering();
                    };
                    
                    uiGmapIsReady.promise(1).then(function(instances) {
                        instances.forEach(function(inst) {
                            var map = inst.map;
                           
                            $scope.search.map.options.mapTypeId = maps.MapTypeId.ROADMAP;
                            
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
                                                        $scope.refineLocation(place);
                                                    } else {
                                                        //$log.debug("GEOCODER ERROR: "+status);
                                                        //TODO handle geocoding error
                                                    }
                                                });
                                            });
                                        } else {
                                            $scope.refineLocation(place);
                                        }
                                    });
                                    
                                };
                            };
                            autocomplete_head.addListener('place_changed', autocompleteChangeListener(autocomplete_head));
                            
                        });
                        
                        
                    });
                    
                    $scope.get_marker_images = function(){ //$log.debug('get_marker_images');
                        
                        var MARKER_IMAGE_COUNT = 19;
                        
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
                        
                        //$log.debug('== renderMap ==');
                        
                        for (var ri=0; ri<$scope.search.product_list.length; ri++){
                            var res = $scope.search.product_list[ri];
                            if (res.locations){
                                res.location_obj = Point(res.locations[0], res.locations[1]);
                                res.images = $scope.marker_images[ri];
                                res.markerId = ri;
                                res.markerOptions = {
                                    icon: res.images.normal,
                                    title: res.plain_summary,
                                    zIndex: ri
                                };    
                            }
                        };
                        
                        //$log.debug(state.getQueryParameter('aroundLatLng'));
                        //$log.debug(state.getQueryParameter('aroundRadius'));
                        
                        //$log.debug("map center: "); 
                        //$log.debug(algoliaToGeoJson(state.getQueryParameter('aroundLatLng')));
                        $scope.search.map.center = algoliaToGeoJson(state.getQueryParameter('aroundLatLng'));
                        var radius = parseFloat(state.getQueryParameter('aroundRadius'))/1000;
                        $scope.search.map.zoom = UtilsService.zoom(radius);
                        
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
                    
//                    $scope.triggerMouseOverGenerator = function (marker) { //$log.debug('triggerMouseOverGenerator');
//                        return function () {
//                            marker.setAnimation(google.maps.Animation.BOUNCE);
//                            google.maps.event.trigger(marker, "mouseover");
//                        };
//                    };
    //
//                    $scope.triggerMouseOutGenerator = function (marker) { //$log.debug('triggerMouseOutGenerator');
//                        return function () {
//                            marker.setAnimation(null);
//                            google.maps.event.trigger(marker, "mouseout");
//                        };
//                    };
                    
                    if ($scope.search.location) {
                        geoc.geocode({address:$scope.search.location}, function(results, status){
                            $scope.$apply(function(){
                                if (status==maps.GeocoderStatus.OK){
                                    //$log.debug("geocoded");
                                    $scope.setOrderByDistance();
                                    $scope.search.center = gmapToGeoJson(results[0].geometry.location);
                                    $scope.search.location_geocoded_deferred.resolve(results, status);
                                } else {
                                    //$log.debug("GEOCODER ERROR: "+status);
                                    $scope.search.location_geocoded_deferred.reject(results, status);
                                }
                            });
                        });
                    } else {
                        $scope.search.location_geocoded_deferred.resolve();
                    }
                    
                    $scope.search.map.loaded = true;

                });
                
                /* 
                 * Filter refinement 
                 */
                
                $scope.onLocationChangeStart = function(event, current, next) { //$log.debug('onLocationChangeStart');
                    
//                    if (!$scope.orig_params_present()) return;
                    
                    if (!$scope.search.location_ui_changed){    
                        
                        var qs = UtilsService.urlEncodeObject($location.search());
                            
                        $scope.search.helper.setState($scope.search_default_state);
                       
                        if ($scope.ui_pristine) {
                            $scope.search.location_geocoded_promise.finally($scope.perform_search);
                            return;
                        }
                        
                        $scope.search.helper.setStateFromQueryString(qs, {
                            prefix: search_params.config.ALGOLIA_PREFIX
                        });
                        
                        var other_params = algoliasearchHelper.url.getUnrecognizedParametersInQueryString(qs, {
                            prefixForParameters: search_params.config.ALGOLIA_PREFIX
                        });
                        
                        $scope.search.location_geocoded = $scope.search.location = 
                            other_params.location_name || search_params.defaults.location;
                        
                        //$log.debug($scope.search.helper.getState());
                        
                        $scope.search.helper.search();
                    } else {
                        $scope.search.location_ui_changed = false;
                    }
                    
                };
                
                $scope.refineQuery = function(){
                    $scope.search.page = 0;
                    $scope.perform_search();  
                };
                
                $scope.refinePrices = function(sliderId){ //$log.debug('refinePrices');
                    
                    var state = $scope.search.helper.getState();
                    var newVal, oldVal;
                    
                    // TODO -1 and '>' are because $location.search() gets confused by '='. Fix this
                    newVal = $scope.search.price.min - 1;
                    if (state.isNumericRefined("price", '>')){
                        oldVal = state.getNumericRefinement("price", '>')[0];
                        if (oldVal != newVal) {
                            $scope.search.helper.removeNumericRefinement("price", '>');
                            $scope.search.helper.addNumericRefinement("price", '>', newVal);
                        }
                    } else {
                        $scope.search.helper.addNumericRefinement("price", '>', newVal);
                    }
                    
                    newVal = $scope.search.price.max + 1;
                    if (state.isNumericRefined("price", '<')){
                        oldVal = state.getNumericRefinement("price", '<')[0];
                        if (oldVal != newVal) {
                            $scope.search.helper.removeNumericRefinement("price", '<');
                            $scope.search.helper.addNumericRefinement("price", '<', newVal);
                        }
                    } else {
                        $scope.search.helper.addNumericRefinement("price", '<', newVal);
                    }
                    
                    $scope.search.page = 0;
                    
                    $scope.perform_search();
                    
                };

                $scope.resetrefineRenter = function(){
                    if (!$scope.search.owner_type.pro)
                        $scope.refineRenterPro(true);
                    if (!$scope.search.owner_type.part)
                        $scope.refineRenterPart(true);
                };

                $scope.refineRenterPart = function(newVal){ //$log.debug('refineRenterPart');
                    var state = $scope.search.helper.getState();
                    if (newVal && !state.isDisjunctiveFacetRefined("pro_owner", false)){
                        $scope.search.helper.addDisjunctiveFacetRefinement("pro_owner", false);
                    }
                    if (!newVal && state.isDisjunctiveFacetRefined("pro_owner", false)){
                        $scope.search.helper.removeDisjunctiveFacetRefinement("pro_owner", false);
                        if (!$scope.search.owner_type.pro){
                            $scope.refineRenterPro(true);
                            return;
                        };
                    }
                    
                    $scope.search.page = 0;
                    
                    $scope.perform_search();
                };
                
                $scope.refineRenterPro = function(newVal){ //$log.debug('refineRenterPro');
                    var state = $scope.search.helper.getState();
                    if (newVal && !state.isDisjunctiveFacetRefined("pro_owner", true)){
                        $scope.search.helper.addDisjunctiveFacetRefinement("pro_owner", true);
                    }
                    if (!newVal && state.isDisjunctiveFacetRefined("pro_owner", true)){
                        $scope.search.helper.removeDisjunctiveFacetRefinement("pro_owner", true);
                        if (!$scope.search.owner_type.part){
                            $scope.refineRenterPart(true);
                            return;
                        };
                    }
                    
                    $scope.search.page = 0;
                    
                    $scope.perform_search();
                };
                
                $scope.noProPartChoice = function(){ //$log.debug('noProPartChoice');
                    return $scope.search.owner_type.pro_count==0 || $scope.search.owner_type.part_count==0;
                };
                
                $scope.categoryName = function(categoryStr){
                    return categoryStr.split('|')[0];
                };
                
                $scope.categoryId = function (categoryStr){
                    return parseInt(categoryStr.split('|')[1]);
                };
                
                $scope.refineCategory = function(path) { //$log.debug('refineCategory');
                    $scope.search.algolia_category_path = path;
                    $scope.search.helper.toggleRefinement("category", $scope.search.algolia_category_path);
                    $scope.clearPropertyRefinements();
                    $scope.search.page = 0;
                    $scope.perform_search();
                };
                
                $scope.refineCategoryClearChildren = function(path) { //$log.debug('refineCategoryClearChildren');
                    $scope.search.helper.toggleRefinement("category", path);
                    $scope.search.helper.toggleRefinement("category", path);
                    $scope.search.page = 0;
                    $scope.perform_search();

                };
                $scope.refineBreadcrumbCategory = function(path) { //$log.debug('refineBreadcrumbCategory');
                    $scope.search.helper.toggleRefinement("category", path);
                    $scope.search.helper.toggleRefinement("category", path);
                    $scope.search.query = '';
                    $scope.search.page = 0;
                    $scope.refineLocation();
                };
                
                $scope.refineProperty = function(prop){
                    // $log.debug("refineProperty");
                    var val = $scope.search[prop.attr_name];
                    if ($scope.search.helper.state.isFacetRefined(prop.attr_name)){
                        $scope.search.helper.removeFacetRefinement(prop.attr_name);   
                    }
                    // FIXME a hack - shoud determine this otherwise
                    if (val !== prop.choices[0]){
                        $scope.search.helper.addFacetRefinement(
                            prop.attr_name, val);   
                    }
                    $scope.perform_search();
                };
                
                /*
                 * Pagination & ordering 
                 */
                
                $scope.nextPage = function(){ //$log.debug('nextPage');
                    $scope.setPage(Math.min($scope.search.page+1, $scope.search.pages_count-1));
                };

                $scope.prevPage = function(){ //$log.debug('prevPage');
                    $scope.setPage(Math.max(0, $scope.search.page-1));
                };
                
                $scope.setPage = function(page){ //$log.debug('setPage');
                    $scope.search.page = page;
                    $scope.perform_search();
                    $window.scrollTo(0, 0);
                };
                
                $scope.setOrdering = function(ordering){ //$log.debug('setOrdering');
//                    $scope.search
//                        .setIndex($scope.get_index());
//                    $scope.search.order_by = ordering;
                    $scope.search.page = 0;
                    $scope.perform_search();
                };
                
                $scope.resetMap = function(){};
                
                $scope.clearPropertyRefinements = function(){
                    if ($scope.search.category && $scope.search.category.properties){
                        var props = $scope.search.category.properties;
                        for (var i=0; i<props.length; i++) {
                            $scope.search.helper.clearRefinements(props[i].attr_name);
                            delete $scope.search[props[i].attr_name];
                        }   
                    }
                };
                
                $scope.clearRefinements = function(){ //$log.debug('clearRefinements');
                    $scope.clearPropertyRefinements();
                    $scope.search.helper.setState($scope.search_default_state);
                    $scope.search.category = null;
//                    $log.debug($scope.search_default_state);
//                    $log.debug($scope.search.helper.getState());
//                    $scope.search.query = "";
                    $scope.search.location = $scope.search.location_geocoded = search_params.defaults.location;
                    $scope.search.helper.search();
                };
                
                
                /* 
                 * Filter rendering
                 * */
                
                $scope.renderPagination = function(result){ //$log.debug('renderPagination');
                    $scope.makePaginationModel(result.nbPages, result.page);
                };
                
                $scope.renderPriceSlider = function(result, state){ //$log.debug('renderPriceSlider');
                    
                    var facetResult = result.getFacetByName("price");
                    if (facetResult){
                        var ref;
                        var statsMin = facetResult.stats.min, statsMax = facetResult.stats.max;
                        
                        $scope.search.price.options.floor = $scope.search.price.min = statsMin;
                        if (state.isNumericRefined("price", '>')){
                            ref = state.getNumericRefinement("price", '>')[0] + 1;
                            $scope.search.price.min = Math.max(statsMin, ref);
                        }
                        
                        $scope.search.price.options.ceil = $scope.search.price.max = statsMax;
                        if (state.isNumericRefined("price", '<')){
                            ref = state.getNumericRefinement("price", '<')[0] - 1;
                            $scope.search.price.max = Math.min(statsMax, ref);
                        }
                        
                        $scope.search.price = $.extend(true, {}, $scope.search.price);        
                    }
                    
                };

                $scope.renderRangeSlider = function(result, state){ //$log.debug('renderRangeSlider');          
                    var radius = state.aroundRadius/1000 || UtilsService.zoom(search_params.defaults.range.ceil);
                    $scope.search.range = $.extend(true, {}, $scope.search.range, {max:radius});    
                    // $timeout(function () {
                    //     $scope.$broadcast('rzSliderForceRender');
                    // });
                };
                
                $scope.renderSearchCategories = function(result, state){ //$log.debug('renderSearchCategories');
                    if (result.hierarchicalFacets && result.hierarchicalFacets[0]) {
                        $scope.search.algolia_category = result.hierarchicalFacets[0];
                        var catFacet = state.hierarchicalFacetsRefinements.category;
                        if (catFacet){
                            var cat = catFacet[0];
                            if (cat){
                                var catparts = cat.split(' > ');
                                var categoryId = $scope.categoryId(catparts[catparts.length-1]);
                                var facets = $scope.search_default_state.getQueryParameter('facets').slice(0);
                                CategoriesService.getCategory(categoryId).then(function(cat){
                                    $scope.search.category = cat;
                                    for (var i=0; i<$scope.search.category.properties.length; i++){
                                        facets.push($scope.search.category.properties[i].attr_name);
                                    };
                                }).finally(function(){
                                    $scope.search.helper.setQueryParameter('facets', facets);
                                    
                                    // Render properties when the category is available
                                    $scope.renderProperties(result, state);
                                  
                                });
                            }   
                        }
                    }
                };
                           
                $scope.renderBreadcrumbs = function(state) { //$log.debug('renderBreadcrumbs');
                    if ("category" in state.hierarchicalFacetsRefinements){
                        $scope.search.breadcrumbs = [];
                        var cat = state.hierarchicalFacetsRefinements.category[0];
                        if (cat){
                            var catparts = cat.split(' > ');
                            $scope.search.leaf_category = $scope.categoryName(catparts[catparts.length-1]);
                            for (var i=0; i< catparts.length; i++){
                                $scope.search.breadcrumbs.push(
                                        {short: catparts[i], long: catparts.slice(0,i+1).join(' > ')});
                            }
                        } else {
                            $scope.search.leaf_category = "";
                        }
                    }
                };
                
                $scope.renderRenterTypes = function(result, state){ //$log.debug('renderRenterTypes');
                    var facetResult = result.getFacetByName("pro_owner");
                    $scope.search.owner_type.pro_count = ('true' in facetResult.data ? facetResult.data.true : 0);
                    $scope.search.owner_type.part_count = ('false' in facetResult.data ? facetResult.data.false : 0);
                    $scope.search.owner_type.pro = state.isDisjunctiveFacetRefined("pro_owner", true);
                    $scope.search.owner_type.part = state.isDisjunctiveFacetRefined("pro_owner", false);
                };
                
                $scope.renderProperties = function(result, state){
                    if ($scope.search.category && 
                                $scope.search.category.properties){
                        var props = $scope.search.category.properties;
                        for (var i=0; i<props.length; i++) {
                            var attr_name = props[i].attr_name;
                            if ((state.facets.indexOf(attr_name)>=0) && state.isFacetRefined(attr_name)){
                                $scope.search[attr_name] = state.getConjunctiveRefinements(attr_name)[0];
                            } else {
                                $scope.search[attr_name] = props[i].default;
                            }
                        };
                    }
                };
                
                $scope.cooldown = false;
                $scope.searchDuringCooldown = false;
                $scope.cooldown_duration = 1000;
                
                $scope.get_query_string_options = function() { //$log.debug('get_query_string_options');
                    return {
                        filters: search_params.config.URL_PARAMETERS, 
                        prefix: search_params.config.ALGOLIA_PREFIX,
                        moreAttributes: {
                            location_name: $scope.search.location
                        }
                    };
                };
                
                $scope.resetCooldown = function(){ //$log.debug('resetCooldown');
                    $scope.cooldown = false;
                    if ($scope.searchDuringCooldown){
                        $scope.searchDuringCooldown = false;
                        $location.search(
                            $scope.search.helper.getStateAsQueryString(
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
                        $location.search($scope.search.helper.getStateAsQueryString(
                            $scope.get_query_string_options()));
                        $timeout($scope.resetCooldown, $scope.cooldown_duration);
                    }
                };
                
                $scope.renderQueryText = function(result) { //$log.debug('renderQueryText');
                    //$log.debug('search_location_ui_changed='+$scope.search.location_ui_changed);
                    if (!$scope.search.location_ui_changed){
                        $scope.search.query = result.query;
                    }
                };
                
                $scope.renderOrdering = function(result) { //$log.debug('renderOrdering');
                    $scope.search.order_by = result.index.substr($scope.search.index.length+1);
                };
                
                /* 
                 * Process search results 
                 */
                
                $scope.processResult = function(result, state){ //$log.debug('processResult');
                    
                    $scope.$apply(function(){
                        //$log.debug(result.page);
                        // $log.debug(result);
                        
                        $scope.search.result_count = result.nbHits;
                        $scope.search.product_list = result.hits;
                        
                        for (var ri=0; ri<$scope.search.product_list.length; ri++){
                            var res = $scope.search.product_list[ri];
                            for (var k in res['_highlightResult']){
                                res["plain_"+k] = res[k];
                                res[k] = res['_highlightResult'][k]['value'];
                            }
                        }
                        
                        $scope.results_per_page = result.hitsPerPage;
                        
                        if ($scope.search.result_count){
                            $scope.search.page = result.page;
                            $scope.search.pages_count = result.nbPages;
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
                        if ($scope.search.map.loaded){
                            $scope.renderMap(result, state);
                        } else {
                            $scope.search.mapLoadedPromise.then(function(){
                                $scope.renderMap(result, state);
                            });
                        }
                        // $scope.renderProperties(result, state);
                        $scope.renderLocation(result, state);
                        
                        //$log.debug($scope.search.product_list);
                        
                        $scope.ui_pristine = false;
                        
                        $scope.request_pending = false;
                        
                    });
                    
                };
                
                $scope.processError = function(error){ //$log.debug('processError');
                    
                    $scope.$apply(function(){
                        $scope.request_pending = false;
                    });
                };
                
                $scope.search.helper.on('result', $scope.processResult)
                    .on('error', $scope.processError);
                
                $scope.resetQuery = function(){ //$log.debug('resetQuery');
                    $scope.search.query = "";
                };
                
                $scope.orig_params = $location.search();
                
                //$log.debug($scope.orig_params);
                $scope.orig_params_present = function(){
                    var orig_params = $location.search();
                    return !!orig_params && Object.keys(orig_params).length > 0;
                }
                //$log.debug('orig_params_present='+$scope.orig_params_present());
                
                $scope.search.algolia_category = null;
                
                $scope.search.breadcrumbs = [];
                
                $scope.search.location_ui_changed = false;
                //$scope.search.query = UtilsService.getParameterByName('q') || "";
                //$scope.search.location = UtilsService.getParameterByName('l') || "";
//                $scope.search.center = search_params.config.COUNTRIES['fr'].center;
                

//                $scope.search.product_list = [];
//                $scope.search.page = 0;
//                $scope.search.result_count = 0;
//                $scope.search.algolia_category_path = "";
//                $scope.search.owner_type = {
//                    pro: true,
//                    part: true,
//                    pro_count: 0,
//                    part_count: 0
//                };
//                $scope.search.breadcrumbs = [];
                $scope.ui_pristine = !$scope.orig_params_present();
//                $scope.price_slider = {
//                    min: 0,
//                    max: 1000,
//                    options: {
//                        floor: 0,
//                        ceil: 1000,
//                        onEnd: $scope.refinePrices,
//                        translate: function(value) {
//                            return value + " €";
//                        }
//                    }
//                };


                $scope.search.range.options = {
                    floor: $scope.search.range.floor,
                    ceil: $scope.search.range.ceil//,
                    // onEnd: $scope.refineRange//,
                    // translate: function(value){
                    //     return $filter("translate")('DISTANCE', {value:value});
                    // }
                    // translate: function(value){
                    //     var koef = search_params.defaults['range'].from_metric;
                    //     return Math.ceil(koef ? (1/koef)*value : value) + 
                    //         ' ' + search_params.defaults['range'].unit;
                    // }
                };      
                
                
                $scope.search.price.options = {
                    floor: $scope.search.price.floor,
                    ceil: $scope.search.price.ceil
                    // onEnd: $scope.refinePrices,
                    // translate: function(value){
                    //     return $filter("translate")('MONEY', {value:value});
                    // }
                    // translate: function(value){
                    //     var koef = search_params.defaults['price'].from_metric;
                    //     return Math.ceil(koef ? (1/koef)*value : value) + 
                    //         ' ' + Currency[search_params.defaults['price'].unit].symbol;
                    // }
                };

                //$log.debug("Added callback:");
                //$log.debug($scope.search.range);    
                
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
                    $scope.search.map_callbacks = false;
                } 

                $scope.$on("$locationChangeStart", $scope.onLocationChangeStart);
                
                $scope.perform_search = function() { //$log.debug('perform_search');
                    if ($scope.request_pending) {
                        return;
                    }
                    $scope.request_pending = true;
                    // TODO remove from here
                    if ($scope.ui_pristine && !$scope.orig_params_present()) {
//                        $scope.$on("$locationChangeStart", $scope.onLocationChangeStart);
                        $scope.orig_params = null;
                    } 
                    $scope.search.location_ui_changed = true;
                    
                    if ($scope.ui_pristine){
                        $scope.search.helper.toggleRefinement("category", $scope.search.algolia_category_path);
                    }
                    
                    //$log.debug($scope.search);
                    
                    $scope.search.helper.setQuery($scope.search.query)
                        .setQueryParameter('aroundLatLng', geoJsonToAlgolia($scope.search.center))
                        .setQueryParameter('aroundRadius', $scope.search.range.max * 1000)
                        .setCurrentPage($scope.search.page)
                        .setIndex($scope.get_index())
                        .search();
                };

                $scope.newSearch = function(){ //$log.debug('newSearch');
                    $scope.search.page = 0;
                    $scope.perform_search();                
                };
                
                $scope.disableForm = function() { //$log.debug('disableForm');
                    setTimeout(function() {
                        $("input, select").attr("disabled", true);
                        $(".jslider-pointer").attr("style", "display: none !important");
                        $("#submitButton").addClass("loading");
                    }, 50);

                };

                $scope.activateLayoutSwitcher();
                
                
            });
            
            
        }]);

    EloueWidgetsApp.controller("CategoryController", ['$scope', '$log', function($scope, $log){
        //$log.debug("CategoryController parent scope:");
        //$log.debug($scope.$parent);
        $scope.$parent.$watch("search.algolia_category", function(category){
            $scope.category = category;
        });
    }]);
    
});
