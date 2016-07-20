define([
    "eloue/app",
    "../../../common/eloue/services/UtilsService",
    "../../../common/eloue/services/CategoriesService",
    "algoliasearch-helper",
    "stacktrace",
    "js-cookie"
], function (EloueWidgetsApp, UtilsService, CategoriesService, algoliasearchHelper, 
                StackTrace, Cookies) {
    "use strict";
    
    var KEY_ENTER = 13;
    var KEY_ESC = 27;
    
    var Point = function(lat, lng){
        return {
            type:"Point",
            coordinates:[lng, lat]
        };
    };
    
    function tupleToGeoJson(t){
        return Point(t[0], t[1]);
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
                                     
    
    EloueWidgetsApp.config(['uiGmapGoogleMapApiProvider', function(uiGmapGoogleMapApiProvider) {
        uiGmapGoogleMapApiProvider.configure({
            v: '3.exp',
            libraries: ['places', 'geometry'],
            language: 'fr-FR',
            region: 'FR'
        });
    }]);
    
    
    function categoryName(categoryStr){
        return categoryStr.split('|')[0];
    };
    
    function categoryId(categoryStr){
        return parseInt(categoryStr.split('|')[1]);
    };
    
    
    EloueWidgetsApp.factory("CategoryService", ["CategoriesService", 
    function(CategoriesService){
        
    }]);
    
    /**
     * Handles the URL bar like filter
     */
    EloueWidgetsApp.factory('SearchLocationService', 
    ["$rootScope", "$location", "$window", "$q", "uiGmapGoogleMapApi", 
    "UtilsService", "GeoService", "SearchService", "$log",
    function($rootScope, $location, $window, $q, uiGmapGoogleMapApi, 
    UtilsService, GeoService, SearchService, $log){
        
        return $q.all({
            ss: SearchService,
            gs: GeoService
        }).then(function(services){
        
            var ss = services.ss, gs = services.gs; 
            
            var s = {
                dontRequest: false
            };
            
            function searchToObject(search){
                return algoliasearchHelper.url
                    .getUnrecognizedParametersInQueryString(search);
            };
            
            $rootScope.$on('$locationChangeStart', function(event, next, current) { //$log.debug('onLocationChangeStart');
                
                if (s.dontRequest){
                    s.dontRequest = false;
                    return;
                }
                
                /**
                 * In case a url is being encoded, replace the
                 * original (unencoded) url with its encoded
                 * version in history
                 */
                if (encodeURI(current) == next){
                    event.preventDefault();
                    ss.replaceLocation = false;
                    s.dontRequest = true;
                    $location.search($location.search());
                    $location.replace();
                    return;
                }
                
                if (ss.replaceLocation){
                    ss.replaceLocation = false;
                    return;
                }
                
                var qs = UtilsService.urlEncodeObject($location.search());
                // Reset helper to defaults
                ss.helper.setState(ss.default_state);
                
                if (ss.ui_pristine()) {
                    
                    ss.search();
                    
                } else {
                    
                    // Restore state
                    ss.helper.setStateFromQueryString(qs, s.get_query_string_options());
                    
                    // Restore custom parameters:
                    var other_params = algoliasearchHelper.url.getUnrecognizedParametersInQueryString(qs, {
                        prefixForParameters: ss.config.ALGOLIA_PREFIX
                    });
                    
                    // - index
                    if (other_params.order_by){
                        /*
                            * accept both Algolia's idx and new order_by param,
                            * order_by overrides idx
                            */ 
                        ss.helper.setIndex(other_params.order_by);   
                    }
                    
                    // - address
                    var address = other_params.location_name || ss.defaults.location;
                    
                    gs.setAddress(address).then(function(gs){
                        ss.page = 0;
                        ss.setPlace(gs.search);
                        ss.search(true);
                    });
                                                         
                }
                
            });
            
            s.get_query_string_options = function(state) { //$log.debug('get_query_string_options');
                
                var res = {
                    filters: ss.config.URL_PARAMETERS, 
                    prefix: ss.config.ALGOLIA_PREFIX,
                    moreAttributes: {
                        location_name: gs.search.location
                    }
                };
                
                var ordering = ss.getOrdering();
                
                if (ordering){
                    res.moreAttributes.order_by = ordering;    
                }
                
                return res;
                
            };
            
            $rootScope.$on('render', function(e, result, state) { //$log.debug('renderLocation');
                
                var qs = ss.helper.getStateAsQueryString(
                        s.get_query_string_options());
                                
                if (!_.isEqual(searchToObject(qs), searchToObject($window.location.hash.substring(2)))){
                    s.dontRequest = !ss.replaceLocation;
                    if (ss.replaceLocation || ss.ui_pristine()){
                        $location.replace();
                    }
                    $location.search(qs);
                } else {
                    ss.replaceLocation = false;
                }
                
                ga('send', 'pageview', $location.url());
                
            });
            
            return s;
                    
        }).catch(function(){
            
            $log.error("Failed to init SearchLocationService");
            
        });;
        
    }]);
    
    EloueWidgetsApp.factory('GeoService', 
    ["$rootScope", "$location", "$q", "uiGmapGoogleMapApi", "UtilsService", "SearchService",
    function($rootScope, $location, $q, uiGmapGoogleMapApi, UtilsService, SearchService){
        
        return $q.all({
            ss: SearchService,
            maps: uiGmapGoogleMapApi
        }).then(function(services){
            
            var maps = services.maps, ss = services.ss;
            
            var config_geocoded_df = $q.defer();
            
            var s = {
                
                maps: maps,
                
                geoc: new maps.Geocoder(),
                                
                config_geocoded: config_geocoded_df.promise,
                
                search: null,
                defaults: null,
                
                isLocationDefault: function(){
                    return s.search.location == s.defaults.location;
                },
                
                setAddress: function(address){
                    return s.addressToModel(address).then(function(model){
                        model.user_address = address;
                        s.search = model;
                        $rootScope.$broadcast("place_changed", s);
                        return s;
                    });
                },
                
                setPlace: function(place){
                    s.search = s.placeToModel(place);
                    $rootScope.$broadcast("place_changed", s);
                    return $q.when(s);
                },
                
                placeToModel: function(place){
                    
                    var res;
                    
                    if (!place){
                        res = {
                            range: s.defaults.range,
                            location: s.defaults.location,
                            location_geocoded: s.defaults.location_geocoded,
                            center: s.defaults.center
                        };
                    } else {
                        var r = "viewport" in place.geometry ? 
                            Math.ceil(maps.geometry.spherical.computeDistanceBetween(
                                    place.geometry.viewport.getNorthEast(),
                                    place.geometry.viewport.getSouthWest())/2000) 
                            : s.defaults.range.options.ceil;
                        res = {
                            range: {
                                max: r,
                                options: {
                                    ceil:r
                                }    
                            },
                            location: place.formatted_address,
                            location_geocoded: place.formatted_address,
                            center: gmapToGeoJson(place.geometry.location)
                        }
                    }
                    
                    return res;

                },
                
                addressToPlace: function(address){
                    
                    var df = $q.defer();
                   
                    s.geoc.geocode({address:address}, function(results, status){
                        
                        if (status==maps.GeocoderStatus.OK){
                            return df.resolve({place:results[0], status:status});
                        } else {
                            return df.reject({place:null, status:status});
                        }

                    });
                    
                    return df.promise;
                   
                },
                
                addressToModel: function(address){
                    
                    return s.addressToPlace(address).then(function(o){
                        return s.placeToModel(o.place);
                    });
                    
                }
                
            };
            
            s.search = ss;
            s.defaults = ss.defaults;
            
            return $q.all([
                s.addressToModel(s.search.location),
                s.addressToModel(s.defaults.location)
            ]).then(function(models){
                s.search = models[0];
                s.defaults = models[1];
                $rootScope.$broadcast("place_changed", s);
                config_geocoded_df.resolve(s);
                return s;
            });
        
        }).catch(function(){
            
            $log.error("Failed to init GeoService");
            
        });
            
    }]);
    
    var EloueFilterController = 
    ["$q", "$scope", "$rootScope", '$attrs', '$filter', '$timeout', '$log', 'SearchService', 'SearchLocationService',
    function ($q, $scope, $rootScope, $attrs, $filter, $timeout, $log, SearchService, SearchLocationService) {
        
        var vm = this;
                            
        vm.value = $scope.value();
        vm.defaults = $scope.defaults();
        vm.attrName = $attrs.attrName;
        
        vm.apply = function(arg){
            $scope.$apply(arg);
        }
        
        vm.on = function(event, cb){
            $scope.$on(event, cb);
        };
        
        vm.render = function(e, result, state){};
                            
        $scope.$on('render', function(e, result, state){
            $scope.$apply(function(){
                vm.empty = !result.nbHits;
                vm.resultCount = result.nbHits;
                vm.results = result.hits;
                vm.render(e, result, state);   
            });
        });
        
        vm.refine = vm.search;
        
        vm.ready = function(){ 
            return false; 
        };
        
        vm.onKeyup = function($event){
            if ($event.which in vm.hotkeys){
                vm.hotkeys[$event.which]();
            }
        };
        
        vm.hotkeys = {};
        vm.hotkeys[KEY_ESC] = function(){
            vm.reset();
        };
        
        vm.filterControllerSetup = $q.all({
            sls:SearchLocationService,
            ss:SearchService
        }).then(function(services){
            
            var sls = services.sls, ss = services.ss;
            
            vm.search = function(){
                ss.setOrdering("");
                ss.page = 0;
                // sls.dontRequest = true;
                ss.search();
            };
            
            vm.clean = function(){
                return !ss.helper.hasRefinements(vm.attrName);
            };
            
            vm.reset = function(){
                ss.helper.clearRefinements(vm.attrName);
                vm.search();
            };
            
            return services;
            
        });
        

    }];
    
    EloueWidgetsApp.directive('eloueFilterWrapper', 
    ['$filter', '$log', 
    function($filter, $log){
        return {
            restrict: 'AE',
            templateUrl:"_filter_wrapper.html",
            scope:{
                value:"&",
                defaults:"&",
                helper:"&"
            },
            transclude: true,
            controller: EloueFilterController,
            controllerAs: "vm",
            link: function(scope, element, attrs, vm, transclude){
                vm.label = attrs.label;
                transclude(scope, function(clone, scope){
                    element.find('div div:last-child').append(clone);
                });                
            }
        }
            
    }]);

    EloueWidgetsApp.directive('eloueFilterWrapperTextfield', 
    ['$filter', '$log', 
    function($filter, $log){
        return {
            restrict: 'A',
            templateUrl:"_filter_wrapper_textfield.html",
            scope:{
                value:"&",
                defaults:"&",
                helper:"&"
            },
            transclude: true,
            controller: EloueFilterController,
            controllerAs: "vm",
            link: function(scope, element, attrs, ctrl, transclude){
                transclude(scope, function(clone, scope){
                    element.prepend(clone);
                });                
            }
        }
    }]);
    
    EloueWidgetsApp.directive('eloueSlider',  
    ['$filter', '$log', 
    function($filter, $log){
        return {
            restrict: 'A',
            require: "eloueFilterWrapper",
            link: function(scope, element, attrs, vm){
                   
                vm.sliderSetup = vm.filterControllerSetup.then(function(services){
                    
                    var ss = services.ss;
                
                    var onEnd;
                    
                    function toMetric(val) {
                        return val===undefined ? val : Math.round(val*(vm.value.from_metric || 1));
                    }
                    
                    function fromMetric(val) {
                        return val===undefined ? val : Math.round(val/(vm.value.from_metric || 1));
                    } 
                    
                    vm.is_range = function(){
                        return 'min' in vm.value;
                    };
                    
                    vm.ready = function(){
                        return 'max' in vm.value && 
                            'ceil' in vm.value.options && 
                            'floor' in vm.value.options;
                    };
                    
                    vm.setValue = function(value, key){
                        var k = key ? key : 'value';
                        if (value !== undefined){
                            $.extend(true, vm[k], {
                                max: fromMetric(value.max),
                                options: {
                                    ceil: fromMetric(value.options.ceil),
                                    floor: fromMetric(value.options.floor)
                                }
                            });
                            if (vm.is_range()){
                                vm[k].min = fromMetric(value.min);
                            }   
                        }
                    };
                    
                    vm.getValue = function (value, key) {
                        var k = key ? key : 'value';
                        var res = {
                            max: toMetric(vm[k].max),
                            options: {
                                ceil: toMetric(vm[k].options.ceil),
                                floor: toMetric(vm[k].options.floor)
                            }
                        };
                        if (vm.is_range()){
                            res.min = toMetric(vm[k].min);   
                        }   
                        return res;
                    };
                    
                    $.extend(true, vm.value, {
                        options:{
                            translate: function (value){
                                return $filter("translate")(attrs.units, {value:value});
                            },
                            onEnd: function (){
                                vm.refine(vm.getValue());
                            }
                        }
                    });
                    
                    return services;
                    
                });
            }
        };
    }]);
    
    EloueWidgetsApp.directive('elouePrice', 
    ['SearchService', '$log', 
    function(SearchService, $log){
        return {
            restrict: 'A',
            'require': "eloueFilterWrapper",
            link: function(scope, element, attrs, vm){
                
                vm.sliderSetup.then(function(services){
                    
                    var ss = services.ss;
                    
                    vm.render = function(e, result, state){
                    
                        if (!result.nbHits){
                            return;
                        }
                        
                        var facetResult = result.getFacetByName("price");
                        
                        if (facetResult){
                            var ref;
                            var statsMin = facetResult.stats.min, statsMax = facetResult.stats.max;
                            var value = vm.getValue();
                            
                            value.options.floor = value.min = statsMin;
                            if (state.isNumericRefined("price", '>')){
                                ref = state.getNumericRefinement("price", '>')[0] + 1;
                                value.min = Math.max(statsMin, ref);
                            }
                            
                            value.options.ceil = value.max = statsMax;
                            if (state.isNumericRefined("price", '<')){
                                ref = state.getNumericRefinement("price", '<')[0] - 1;
                                value.max = Math.min(statsMax, ref);
                            }
                            
                            vm.setValue(value);
    
                        }
                        
                    };
                
                    vm.refine = function(value){ //$log.debug('refinePrices');
                        
                        var state = ss.helper.getState();
                        var newVal, oldVal;
                        
                        // TODO -1 and '>' are because $location.search() gets confused by '='. Fix this
                        newVal = value.min - 1;
                        if (state.isNumericRefined("price", '>')){
                            oldVal = state.getNumericRefinement("price", '>')[0];
                            if (oldVal != newVal) {
                                ss.helper.removeNumericRefinement("price", '>');
                                ss.helper.addNumericRefinement("price", '>', newVal);
                            }
                        } else {
                            ss.helper.addNumericRefinement("price", '>', newVal);
                        }
                        
                        newVal = value.max + 1;
                        if (state.isNumericRefined("price", '<')){
                            oldVal = state.getNumericRefinement("price", '<')[0];
                            if (oldVal != newVal) {
                                ss.helper.removeNumericRefinement("price", '<');
                                ss.helper.addNumericRefinement("price", '<', newVal);
                            }
                        } else {
                            ss.helper.addNumericRefinement("price", '<', newVal);
                        }
                        
                        ss.helper.setCurrentPage(0)
                        
                        vm.search();
                        
                    };
                     
                });
               
            }
        };
    }]);
    
    EloueWidgetsApp.directive('eloueDistance',  
    ['$q', 'SearchService', 'GeoService', '$log', 
    function($q, SearchService, GeoService, $log){
        return {
            restrict: 'A',
            'require': "eloueFilterWrapper",
            link: function ($scope, $element, $attrs, vm) {
                
                $q.all({
                    gs:GeoService,
                    sliderSetup:vm.sliderSetup
                }).then(function(services){
                    
                    var ss = services.sliderSetup.ss, gs = services.gs;
                    
                    vm.refine = function(value){ //$log.debug('refineDistance')
                        ss.helper.setQueryParameter('aroundRadius', value.max * 1000);
                        vm.search();
                    };
                                  
                    vm.reset = function(){
                        ss.helper.setQueryParameter('aroundRadius', 
                            (vm.value.options.ceil || vm.defaults.max) * 1000);
                        vm.search();
                    };
                    
                    $scope.$on('place_changed', function(e, gs){
                        vm.setValue(gs.search.range);  
                        vm.setValue(gs.search.defaults, 'defaults');
                    });
                
                    vm.render = function(e, result, state){ //$log.debug('renderRangeSlider');
                        if (!result.nbHits){
                            return;
                        }
                        var val = vm.getValue();
                        val.max = state.aroundRadius/1000 || vm.value.options.ceil || vm.defaults.max;  
                        vm.setValue(val);  
                    };
                    
                    vm.clean = function(){
                        return vm.value.max == vm.value.options.ceil;
                    };
                    
                    vm.setValue(gs.search.range);
                    
                    return services;
                    
                });
                
            }
        };
    }]);
    
    EloueWidgetsApp.directive('elouePropart',  
    ['SearchService', '$log', 
    function(SearchService, $log){
        return {
            restrict: 'A',
            'require': 'eloueFilterWrapper',
            link: function($scope, $element, $attrs, vm){
                
                vm.filterControllerSetup.then(function(services){
                    
                    var ss = services.ss;

                    vm.render = function(e, result, state){ //$log.debug('renderRenterTypes');
                        if (!result.nbHits){
                            return;
                        }
                        var facetResult = result.getFacetByName("pro_owner");
                        vm.value.pro_count = ('true' in facetResult.data ? facetResult.data.true : 0);
                        vm.value.part_count = ('false' in facetResult.data ? facetResult.data.false : 0);
                        vm.value.pro = !state.isDisjunctiveFacetRefined("pro_owner") 
                            || state.isDisjunctiveFacetRefined("pro_owner", true);
                        vm.value.part = !state.isDisjunctiveFacetRefined("pro_owner") 
                            || state.isDisjunctiveFacetRefined("pro_owner", false);
                    };
                    
                    vm.refineRenterPart = function(newVal){ //$log.debug('refineRenterPart');
                        var state = ss.helper.getState();
                        
                        ss.helper.removeDisjunctiveFacetRefinement("pro_owner");
                        if (!newVal) {
                            ss.helper.addDisjunctiveFacetRefinement("pro_owner", true);
                        }
                        
                        vm.search();
                    };
                    
                    vm.refineRenterPro = function(newVal){ //$log.debug('refineRenterPro');
                        var state = ss.helper.getState();
                        
                        ss.helper.removeDisjunctiveFacetRefinement("pro_owner");
                        if (!newVal) {                
                            ss.helper.addDisjunctiveFacetRefinement("pro_owner", false);
                        }
                        
                        vm.search();
                    };
                    
                    vm.ready = function(){
                        return true;
                    };
                    
                    vm.noProPartChoice = function(){ //$log.debug('noProPartChoice');
                        return vm.value.pro_count==0 || vm.value.part_count==0;
                    };
 
                });
  
            }
    
        };
    }]);
    
  
    EloueWidgetsApp.directive('eloueQuery',  
    ['SearchService', '$timeout', '$log', 
    function(SearchService, $timeout, $log){
        
        return {
            restrict: 'A',
            'require': 'eloueFilterWrapperTextfield',
            link: function ($scope, $element, $attrs, vm) {
                
                /*
                $scope.$on('render', function(e, result, state) { //$log.debug('renderQueryText');
                    //$log.debug('search_location_ui_changed='+$scope.search.location_ui_changed);
                    if (!$scope.search.location_ui_changed){
                        $scope.search.query = result.query;
                    }
                });
                */
                
                // TODO don't render if focused
                
                vm.filterControllerSetup.then(function(services){
                    
                    var ss = services.ss;
                    
                    vm.refine = function() {
                        if (vm.debouncePromise){
                            $timeout.cancel(vm.debouncePromise);
                        }
                        vm.debouncePromise = $timeout(function() {
                            vm.debouncePromise = null;
                            ss.helper.setQuery(vm.value);
                            ss.page = 0;
                            ss.search();
                        }, vm.debounceDelay);
                    };
                                 
                    vm.clean = function(){
                        return !(ss.helper.state.query || vm.value);
                    };
                    
                    vm.reset = function() {
                        vm.value = vm.default;
                        $element.children('input')[0].focus();
                        ss.helper.setQuery(vm.default);
                        vm.search();
                    };
                            
                });

                vm.focused = true;
                
                vm.debouncePromise = null;
                vm.debounceDelay = parseInt($attrs.debounceDelay);
                
                vm.render = function(e, result, state) { //$log.debug('renderQueryText');
                    if (!vm.focus){
                        vm.value = result.query;
                        // TODO fix reset
                    }
                };

                
            }
        };
    }]);

    
    EloueWidgetsApp.directive('eloueLocation',  
    ["$q", 'GeoService', "SearchService", '$log', 
    function($q, GeoService, SearchService, $log){
        return {
            restrict: 'A',
            'require': 'eloueFilterWrapperTextfield',
            link:  function ($scope, $element, $attrs, vm) {                
                
                
                $q.all({
                    ss:SearchService,
                    gs:GeoService
                }).then(function(services){
                    
                    var gs = services.gs, ss = services.ss;

                    var maps = gs.maps;
                    
                    var placeInputHead = $element.children('input')[0];

                    var ac_params = {
                        //componentRestrictions: {country: 'fr'}
                    };
                    
                    var ac = new maps.places.Autocomplete(placeInputHead, ac_params);
                    
                    ac.addListener('place_changed', function(){
                        
                        vm.apply(function(){
                            
                            var place = ac.getPlace();
                            
                            ('geometry' in place && 'location' in place.geometry ? 
                                gs.setPlace(place):
                                gs.setAddress(place.formatted_address)).then(vm.placeChanged);
                                
                        });
                        
                    });
                    
                    vm.refine = function(model){ //$log.debug('refineLocation');
                        
                        ss.setPlace(model);

                        ss.page = 0;
                        ss.search();
                        
                    };
                    
                    vm.render = function(e, result, status) {
                        vm.value = vm.focus ? "" : gs.search.location;
                    };
                    
                    vm.reset = function() {
                        gs.setAddress(vm.defaults)
                            .then(vm.placeChanged);
                        // $element.children('input')[0].focus();
                        // vm.refine(gs.search);
                    };
                    
                    vm.clean = function() {
                        return gs.search.location === vm.defaults;
                    };
                    
                    vm.onFocus = function(){
                        vm.value = "";
                        vm.focus = true;
                    };
                    
                    vm.onBlur = function(){
                        vm.value = gs.search.location;
                        vm.focus = false;
                    };
                    
                    vm.placeChanged = function(gs){
                        vm.refine(gs.search);
                    };
                    
                    // TODO select on enter
                    // vm.hotkeys[KEY_ENTER] = function(){
                    //     gs.setAddress(vm.value);  
                    // };
                    
                });
                
            }
        };
    }]);

    EloueWidgetsApp.directive('eloueCategories',  
    ['SearchService', '$log', 
    function(SearchService, $log){
        return {
            restrict: 'A',
            'require': 'eloueFilterWrapper',
            link: function ($scope, $element, $attrs, vm) {
                
                vm.filterControllerSetup.then(function(services){
                    
                    var ss = services.ss;
                    
                    vm.categoryName = categoryName;
                    
                    vm.refine = function(path) { //$log.debug('refineCategory');
                        vm.value.algolia_category_path = path;
                        if (!vm.value.algolia_category_path){
                            ss.helper.clearRefinements("category");
                        } else {
                            ss.helper.toggleRefinement("category", vm.value.algolia_category_path);
                        }
                        // $scope.clearPropertyRefinements();
                        vm.search();
                    };
                    
                    vm.render = function(e, result, state){ //$log.debug('renderSearchCategories');
                        if (!result.nbHits){
                            return;
                        }
                        // if (result.nbHits) {
                        vm.value = result.hierarchicalFacets[0];
                            // var catFacet = state.hierarchicalFacetsRefinements.category;
                            // if (catFacet){
                            //     var cat = catFacet[0];
                            //     if (cat){
                            //         var catparts = cat.split(' > ');
                            //         var categoryId = $scope.categoryId(catparts[catparts.length-1]);
                            //         if (categoryId==="number"){
                            //             var facets = $scope.search.default_state.getQueryParameter('facets').slice(0);
                            //             CategoriesService.getCategory(categoryId).then(function(cat){
                            //                 $scope.search.category = cat;
                            //                 for (var i=0; i<$scope.search.category.properties.length; i++){
                            //                     facets.push($scope.search.category.properties[i].attr_name);
                            //                 };
                            //             }).finally(function(){
                            //                 $scope.search.helper.setQueryParameter('facets', facets);
                                            
                            //                 // Render properties when the category is available
                            //                 $scope.renderProperties(result, state);
                                        
                            //             });   
                            //         }
                            //     }   
                            // }
                        // }
                    };
                    
                    var superClean = vm.clean;
                    vm.clean = function(){
                        return superClean() || !ss.helper.state.hierarchicalFacetsRefinements[$attrs.attrName][0];
                    };
                    
                    vm.ready = function(){
                        return true;
                    };
                    
                    vm.reset = function(){
                        ss.helper.clearRefinements($attrs.attrName);
                        vm.leaf_category = "";
                        vm.search();
                    };
                    
                     
                });
                
            }
        };
    }]);    
    
    
    EloueWidgetsApp.directive('eloueMap',  
    ['UtilsService', 'GeoService', 'SearchService', "$q", '$document', '$log', 
    function(UtilsService, GeoService, SearchService, $q, $document, $log){
                               
        var staticUrl = "/static/", scripts = $document[0].getElementsByTagName("script"), i, j, l,
            product, image, imageHover, myLatLng, marker;
        for (i = 0, l = scripts.length; i < l; i += 1) {
            if (scripts[i].getAttribute("data-static-path")) {
                staticUrl = scripts[i].getAttribute("data-static-path");
                break;
            }
        };
       
        return {
            restrict: 'A',
            'require': 'eloueFilterWrapper',
            link:  function ($scope, $element, $attrs, vm) {    
                
                $q.all({
                    ss:SearchService,
                    gs:GeoService
                }).then(function(services){
                    
                    var ss = services.ss;
                    
                    var gs = services.gs, ss = services.ss;
                    var maps = gs.maps;
                    
                    function getMarkerImages(){ //$log.debug('get_marker_images');
                        
                        var MARKER_IMAGE_COUNT = 19;

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
                    
                    
                    vm.value =  {
                        loaded: true,
                        zoom: UtilsService.zoom(ss.range.max),
                        center: ss.center,
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
                        marker_event_handlers:{
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
                        },
                        control: {}
                    };
                    
                    vm.marker_images = getMarkerImages();
                             
                    vm.render = function(e, result, state) { //$log.debug('renderMap');
                        
                        for (var ri=0; ri<vm.results.length; ri++){
                            var res = vm.results[ri];
                            if (res.locations){
                                res.location_obj = Point(res.locations[0], res.locations[1]);
                                res.images = vm.marker_images[ri];
                                res.markerId = ri;
                                res.markerOptions = {
                                    icon: res.images.normal,
                                    title: res.plain_summary,
                                    zIndex: ri
                                };
                            }
                        };
                        
                        vm.value.center = algoliaToGeoJson(state.getQueryParameter('aroundLatLng'));
                        vm.value.zoom = UtilsService.zoom(
                            parseFloat(state.getQueryParameter('aroundRadius'))/1000);
                        
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
                    
                    
                    vm.value.loaded = true;
                    
                    vm.ready = function(){
                        return vm.value.loaded;
                    };

                });    
            }
        };
    }]);
    
    
    EloueWidgetsApp.directive('elouePropertyDropdownFilter', 
    function(){
        return {
            template: '<label class="caption", for="{{proto.attr_name+proto.id}}">{{proto.name}}</label>'+
                    '<select id="{{proto.attr_name+proto.id}}" ng-model="value" '+
                      'ng-options="choice for choice in proto.choices" '+
                      'data-placeholder="{{proto.name}}" '+
                      'class="form-control" eloue-chosen></select>',
            restrict: 'A',
            'require': 'ngModel', 
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
    
    
    EloueWidgetsApp.controller('elouePaginationController', 
    ['$scope', '$window', 'SearchService',
    function($scope, $window, SearchService){
        
        SearchService.then(function(ss){
            
            $scope.makePaginationModel = function(nbPages, page){
                $scope.page = Math.min(nbPages-1, Math.max(0, page));
                var PAGINATION_WINDOW_SIZE = ss.config.PAGINATION_WINDOW_SIZE;
                if (nbPages < PAGINATION_WINDOW_SIZE){
                    $scope.pages_range = new Array(nbPages);
                    for (var i=0; i<nbPages; i++){
                        $scope.pages_range[i] = i;
                    }
                } else {
                    if ($scope.page > nbPages/2){
                        var last = Math.min(page+Math.ceil(PAGINATION_WINDOW_SIZE/2+1), nbPages-1);    
                        var first = Math.max(0, last-PAGINATION_WINDOW_SIZE);
                    } else {
                        var first = Math.max(0, page-Math.floor(PAGINATION_WINDOW_SIZE/2+1));
                    }
                    $scope.pages_range = new Array(PAGINATION_WINDOW_SIZE);
                    for (var i=0; i<PAGINATION_WINDOW_SIZE; i++){
                        $scope.pages_range[i] = first+i;
                    }
                }
            };
            
            $scope.setPage = function(page){ //$log.debug('setPage');
                ss.page = page;
                ss.search();
                $window.scrollTo(0, 0);
            };
                            
            $scope.nextPage = function(){ //$log.debug('nextPage');
                $scope.setPage(Math.min($scope.page+1, $scope.pages_count-1));
            };

            $scope.prevPage = function(){ //$log.debug('prevPage');
                $scope.setPage(Math.max(0, $scope.page-1));
            };
            
            $scope.$on('render', function(e, result){ //$log.debug('renderPagination');
                $scope.pages_count = result.nbPages;
                $scope.page = result.page;
                $scope.makePaginationModel(result.nbPages, result.page);
            });    
               
        });
        
    }]);
    
    EloueWidgetsApp.service('SearchService', 
    ['$q', '$rootScope', '$window', '$location', 'algolia', '$log',
    function($q, $rootScope, $window, $location, algolia, $log){
        
        var sd = $q.defer();
        
        $rootScope.$on('config', function(e, config){
            
            if (!config){
                sd.reject();    
            } else {
                sd.resolve(config);
            };
            
        });
        
        return sd.promise.then(function(sp){
            
            var s = {
                
                result: {ordering:""},
                
                setArea: function(model){
                    s.helper.setQueryParameter('aroundRadius', model.range.max * 1000);
                    s.helper.setQueryParameter('aroundLatLng', geoJsonToAlgolia(model.center));
                },
                
                setOrdering: function(ordering){
                    s.helper.setIndex(!!ordering ? s.index+"_"+ordering : s.index);
                },
                
                getOrdering: function(){
                    return s.result.index.slice(s.index.length+1, s.result.index.length);
                },
                
                reset: function (){
                    s.helper.setState(s.default_state);
                },
                
                processResult: function(result, state){
                    s.result = result;
                    for (var ri=0; ri<result.hits.length; ri++){
                        var res = result.hits[ri];
                        for (var k in res._snippetResult){
                            res["plain_"+k] = res[k];
                            res[k] = res._snippetResult[k]['value'];
                        }
                    }
                    $rootScope.$broadcast('render', result, state);
                },
                
                processError: function(){
                    
                }, 
                
                search: function(replaceLocation){
                    s.replaceLocation = replaceLocation || false;
                    s.helper.setCurrentPage(s.page);
                    s.helper.search();
                },
                
                ui_pristine: function(){
                    var orig_params = $location.search();
                    return !orig_params || Object.keys(orig_params).length == 0;
                },
                
                setPlace: function(model){ //$log.debug('refineLocation');
                    
                    if (model.location !== s.defaults.location){
                        s.setOrdering("distance");
                    } else if (s.getOrdering()=="distance"){
                        s.setOrdering("");
                    };
                    
                    s.helper.setQueryParameter('aroundLatLng', geoJsonToAlgolia(model.center));
                    s.helper.setQueryParameter('aroundRadius', model.range.max * 1000);
                    
                },
                
            };
                
            // Patch parameters
            // TODO move to settings.py
            sp.config.PARAMETERS.attributesToRetrieve = ["summary", "django_id", "username", 
                "location", "locations", "city", "zipcode", "owner_url", "owner_avatar", "url", "price", "profile", 
                "vertical_profile", "thumbnail", "comment_count", "average_rate"];
            sp.config.PARAMETERS.snippetEllipsisText = "&hellip;";
                
            sp.init.center = tupleToGeoJson(sp.init.center);
            sp.defaults.center = tupleToGeoJson(sp.defaults.center);
            
            $.extend(true, s, sp.defaults, sp.init, {config:sp.config});
            s.defaults = sp.defaults;
            
            s.index = sp.config.MASTER_INDEX;
            s.range.options = {
                floor: s.range.floor,
                ceil: s.range.ceil,
            };      
            s.price.options = {
                floor: s.price.floor,
                ceil: s.price.ceil
            };
                                
            // Init client
            var client = algolia.Client(sp.config.ALGOLIA_APP_ID, sp.config.ALGOLIA_KEY);
            s.client = client;
            
            // Init helper
            var helper = algoliasearchHelper(client, s.orderedIndex, sp.config.PARAMETERS)
                            .on('result', s.processResult)
                            .on('error', s.processError);
            s.helper = helper;
            s.setOrdering(s.ordering);
            
            // Preset filters
            //TODO remove by not indexing
            helper.addDisjunctiveFacetRefinement("sites", s.site);
            helper.addFacetRefinement("is_archived", false);
            helper.addFacetRefinement("is_allowed", true);
            
            s.setArea(s);
            
            // Save default helper state
            s.default_state = helper.getState();
            
            return s;
            
        }).catch(function(){
            
            $log.error("Failed to init SearchService");
            
        });
        
    }]);
    
    
    /**
     * Controller to run scripts necessary for product list page.
     */
    EloueWidgetsApp.controller("AlgoliaProductListCtrl", [
        "$scope",
        "$rootScope",
        "$window",
        "$timeout",
        "$document",
        "$q",
        "$log",
        "SearchLocationService",
        "GeoService",
        "SearchService",
        function ($scope, $rootScope, $window, $timeout, $document, $q, $log, 
                SearchLocationService, GeoService, SearchService) {

            var unsubscribe = $scope.$watch('search_params', function(search_params){
                unsubscribe();  
                $rootScope.$broadcast('config', search_params);
            });
            
            $q.all({
                ss: SearchService,
                gs: GeoService
            }).then(function(services){
                 
                var gs = services.gs, ss = services.ss;
                 
                $scope.search = ss;
                $scope.defaults = ss.defaults;
                $scope.ui_pristine = ss.ui_pristine();
                
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
                
                $scope.ordering = "";
                $scope.setOrdering = function(ordering){ //$log.debug('setOrdering');
                    ss.setOrdering(ordering);
                    ss.search();
                };
                
                
                $scope.clearPropertyRefinements = function(){
                    if ($scope.search.category && $scope.search.category.properties){
                        var props = $scope.search.category.properties;
                        for (var i=0; i<props.length; i++) {
                            $scope.search.helper.clearRefinements(props[i].attr_name);
                            delete $scope.search[props[i].attr_name];
                        }   
                    }
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
                
                
                $scope.$on('render',  function(e, result) { //$log.debug('renderOrdering');
                    $scope.enableDistance = !gs.isLocationDefault();
                    $scope.ordering = ss.getOrdering();
                    $scope.location = gs.location;
                    $scope.result_count = result.nbHits;
                    $scope.query = result.query;
                    $scope.product_list = result.hits;
                    $scope.results_per_page = result.hitsPerPage;
                    $scope.ui_pristine = false;
                });
                
                
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
                
                $scope.$on('perform_search', ss.search());

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
    
});
