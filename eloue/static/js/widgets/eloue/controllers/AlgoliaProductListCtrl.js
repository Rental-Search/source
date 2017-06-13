define([
    "eloue/app",
    "../../../common/eloue/services/UtilsService",
    "../../../common/eloue/services/CategoriesService",
    "algoliasearch-helper",
    "stacktrace",
    "../i18n",
    "js-cookie",
], function (EloueWidgetsApp, UtilsService, CategoriesService, algoliasearchHelper, 
                StackTrace){ //,Cookies) {
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
    
    // var el = Cookies.get("eloue_el");
    
    // function hasStorage(){
    //     return typeof(Storage) !== 'undefined';
    // };
    
    // function cleanup(){
    //     if (hasStorage()){
    //         var i = sessionStorage.length;
    //         while (i--){
    //             var key = sessionStorage.key(i);
    //             if (key.match(/^eloue_err_.*/g)){
    //                 sessionStorage.removeItem(key);
    //             }
    //         }
    //     } 
    // };
    
    // if (el){
    //     EloueWidgetsApp.factory('$exceptionHandler', function() {
            
    //         function frameKey(f) {
    //             return f.functionName+'@'+f.fileName+':'+f.lineNumber+':'+f.columnNumber;
    //         };
            
    //         var ec = parseInt(Cookies.get('eloue_ec')) || 0;
            
    //         if (!ec){
    //             cleanup();
    //         }
            
    //         var log;
            
    //         if (hasStorage()){
    //             log = function(trace){
    //                 var topFrame = trace[0];
    //                 var key = 'eloue_err_'+frameKey(topFrame);
    //                 var exceptionCount = parseInt(Cookies.get('eloue_ec')) || 0;
    //                 if (exceptionCount<parseInt(el) && !(sessionStorage.getItem(key))){
    //                     Cookies.set('eloue_ec', exceptionCount+1);
    //                     sessionStorage.setItem(key,1);
    //                     StackTrace.report(trace, "/logs/").then(function(resp){
    //                     }).catch(function(resp){
    //                     });
    //                 };
    //             };
    //         } else {
    //             log = function(trace){
    //                 var topFrame = trace[0];
    //                 var key = 'eloue_err_'+frameKey(topFrame);
    //                 var exceptionCount = Cookies.get('eloue_ec');
    //                 if (!exceptionCount){
    //                     Cookies.set('eloue_ec', 1);
    //                     StackTrace.report(trace, "/logs/").then(function(resp){
    //                     }).catch(function(resp){
    //                     });
    //                 };
    //             };
    //         }
            
    //         return function(exception, cause) {                
    //             StackTrace.fromError(exception, {offline:false})
    //                 .then(log).catch(function(trace){});
    //         };
            
    //     });    
    // } else {
    //     cleanup();
    // }
                
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
                                     
    
    EloueWidgetsApp.config(
    ['uiGmapGoogleMapApiProvider', 'MAP_CONFIG', 
    function(uiGmapGoogleMapApiProvider, MAP_COFNIG) {
        
        // TODO a hack to get the language 
        var lang = angular.element(document)[0].documentElement.lang;
        
        var conf = $.extend({
            v: '3.exp',
            libraries: ['places', 'geometry'],
        }, MAP_COFNIG[lang]);
        
        uiGmapGoogleMapApiProvider.configure(conf);

    }]);
    
    
    function categoryName(categoryStr){
        return categoryStr.split('|')[0];
    };
    
    function categoryId(categoryStr){
        return parseInt(categoryStr.split('|')[1]);
    };

    function categoryAttributeName(){
        var lang = angular.element(document)[0].documentElement.lang;
        return "category."+lang;
    }


   
    /**
     * Wraps the Algolia helper and stores additional search state.
     * Configures the helper and sets default search parameters from
     * JSON search_config attribute on the application root element.
     */
    EloueWidgetsApp.service('SearchService', 
    ['$q', '$rootScope', '$window', '$location', 
    'algolia', 'CategoriesService', '$log', '$sce',
    function($q, $rootScope, $window, $location, 
    algolia, CategoriesService, $log, $sce){
        
        var sd = $q.defer();
        
        // Receive the search_config
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
                    return s.helper.state.index.slice(s.index.length+1);
                },
                
                reset: function (){
                    s.helper.setState(s.default_state);
                },
                
                processResult: function(result, state){
                    s.result = result;
                    for (var ri=0; ri<result.hits.length; ri++){
                        var res = result.hits[ri];
                        for (var k in res._snippetResult){
                            if (res[k]){
                                res[k+"_plain"] = res[k];  
                            }
                            res[k] = $sce.trustAsHtml(
                                res._snippetResult[k].value);
                        }
                        for (var k in res._highlightResult){
                            if (res[k]){
                                res[k+"_plain"] = res[k];  
                            }
                            res[k] = $sce.trustAsHtml(
                                res._highlightResult[k].value);
                        }   
                    }
                    $rootScope.$broadcast('render', result, state);
                },
                
                processError: function(){
                    
                },
                
                search: function(noProgress){
                    if (!noProgress) {
                        NProgress.begin();
                    };
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
                
                getDefaultFacetsList: function(){
                    return s.default_state.getQueryParameter('facets').slice(0);
                },
                
                categoryHasProperties: function(){
                    return s.category.properties && s.category.properties.length;    
                },
                             
                clearCategoryRefinements: function(){
                    for (var i=0; i<s.category.properties.length; i++){
                        var attr_name = s.category.properties[i].attr_name;
                        try {
                            if (s.helper.state.isFacetRefined(attr_name)){
                                s.helper.removeFacetRefinement(attr_name);
                            }      
                        } catch(e) {}
                    }
                
                },
                
                retreiveCategoryByPath: function(path){
                    var catparts = path.split(' > ');
                    var id = categoryId(catparts[catparts.length-1]);
                    return CategoriesService.getCategory(id);
                },
                
                setCategory: function(category){
                    
                    // Remove old category
                    if (s.category && s.categoryHasProperties()) {
                        s.clearCategoryRefinements();
                    }
                    s.category = category;
                    
                    // Set facets for the new category
                    var facets = s.getDefaultFacetsList();
                    if (s.category && s.categoryHasProperties()){
                        for (var i=0; i<category.properties.length; i++){
                            facets.push(category.properties[i].attr_name);
                        };      
                    }
                    s.helper.setQueryParameter('facets', facets);
                    
                    $rootScope.$broadcast("categoryChanged", category);
                    
                },
                
                updateCategoryFromPath: function(path){
                    return (path ?
                         s.retreiveCategoryByPath(path):
                         $q.when(null)).then(s.setCategory);
                }
                
            };
                
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
            
            // Add a rootPath if there is a single root category
            if (s.defaults.category) {
                for (var i=0; i<sp.config.PARAMETERS.hierarchicalFacets.length; i++){
                    if (categoryAttributeName()==sp.config.PARAMETERS.hierarchicalFacets[i].name) {
                        sp.config.PARAMETERS.hierarchicalFacets[i].rootPath =
                            s.defaults.category.algolia_path;
                        break;
                    }
                }
            }
            
            // Init helper
            var helper = algoliasearchHelper(client, s.orderedIndex, sp.config.PARAMETERS)
                            .on('result', s.processResult)
                            .on('error', s.processError);
            s.helper = helper;
            s.getQuery = helper.getStateAsQueryString;

            s.setOrdering(s.ordering);
            s.helper.setQuery(s.query);
            
            // Preset filters
            //TODO remove by not indexing
            helper.addDisjunctiveFacetRefinement("sites", s.site);
            helper.addFacetRefinement("is_archived", false);
            helper.addFacetRefinement("is_allowed", true);
            
            s.setArea(s);
            
            // Save default helper state
            s.default_state = helper.getState();
            
            s.setCategory(s.category);
            
            NProgress.move(0.3);
            
            return s;
            
        }).catch(function(){
            
            $log.error("Failed to init SearchService");
            
        });
        
    }]);
    
    
    /**
     * Handles the URL bar like other filters:
     *  * changing the URL triggers requests,
     *  * search responses trigger url rendering
     */
    EloueWidgetsApp.factory('SearchLocationService', 
    ["$q", "$rootScope", "$location", "$window", "$timeout", "uiGmapGoogleMapApi", 
    "UtilsService", "GeoService", "SearchService", "$log",
    function($q, $rootScope, $location, $window, $timeout, uiGmapGoogleMapApi, 
    UtilsService, GeoService, SearchService, $log){
        
        return $q.all({
            ss: SearchService,
            gs: GeoService
        }).then(function(services){
        
            var ss = services.ss, gs = services.gs;

            var s = {
                getQueryString: function(){
                    return decodeURI($window.location.hash.substring(2));
                },
                action:{
                    RENDER:"r",
                    VALIDATE:"v"
                }
            };
            
            function searchToObject(search){1
                return algoliasearchHelper.url
                    .getUnrecognizedParametersInQueryString(search);
            }
            
            function categoryPathFromParams(params){
                return ('sp_hFR' in params) ? params.sp_hFR[categoryAttributeName()][0] : null;
            }
            
            function getFilters(category){
                var moreFilters = ss.config.URL_PARAMETERS.slice(0);
                // Don't show parameter default category
                if (!category || ss.defaults.category && category.algolia_path == ss.defaults.category.algolia_path){
                    moreFilters.splice(moreFilters.indexOf("attribute:category"),1);
                }
                // Add parameters for properties
                if (category && category.properties) {
                    for (var i=0; i<category.properties.length; i++){
                        moreFilters.push('attribute:'
                            +category.properties[i].attr_name);
                    }   
                }
                return moreFilters;
            }
            
            $rootScope.$on('$locationChangeStart', function(event, next, current) { //$log.debug('onLocationChangeStart');
                
                var other_params = algoliasearchHelper.url
                    .getUnrecognizedParametersInQueryString(next, {
                        prefixForParameters: ss.config.ALGOLIA_PREFIX
                    });
                
                /**
                 * Handle following cases of URL change:
                 */
                if (other_params.action){
                    
                    var newqs = ss.helper.getStateAsQueryString(
                        s.getQueryOptions(null, getFilters(ss.category)));
                    
                //  - after URL validation - set URL and search
                    if (other_params.action == s.action.VALIDATE){
                        $location.search(newqs);
                        ss.helper.search();
                        return;
                //  - during rendering - set URL only
                    } else if (other_params.action == s.action.RENDER) {
                        $location.search(newqs);
                        return;
                    } else {
                        throw "Action not supported";
                    }
                
                //  - on first page load, if there is no hash
                } else if (ss.ui_pristine()) {
                    
                    // Reset helper to defaults
                    // ss.reset();
                    ss.search();
                
                //  - after user modifies URL/navigates by back/forward, on
                //    first page load with hash - validate URL
                } else {
                    
                    NProgress.begin();
                    
                    var qs = s.getQueryString();
                    var address = other_params.location_name || ss.defaults.location;
                    var path = categoryPathFromParams(other_params);
                    
                    // Validate place and category
                    $q.all({
                        place:gs.addressToPlace(address),
                        category:(path ? 
                            ss.retreiveCategoryByPath(path) : 
                            $q.when(null))
                    }).then(function(res){
                        
                        NProgress.move(0.6);
                        
                        var place = res.place.place, category = res.category;
                        
                        // Validate algolia parameters
                        ss.reset();
                        ss.helper.setStateFromQueryString(qs, 
                            s.getQueryOptions(null, getFilters(category)));
                        
                        // Set validated place and category
                        ss.setCategory(category);
                        gs.setPlace(place);
                        ss.setPlace(gs.search);
                        
                        // Set ordering
                        if (other_params.order_by){
                            /*
                             * accept both Algolia's idx and new order_by param,
                             * order_by overrides idx
                             */ 
                            ss.setOrdering(other_params.order_by); 
                        }
                        
                        // FIXME page is not restored
                        ss.helper.setPage(other_params.sp_p);
                        
                        // Replace user URL with validated URL
                        var newqs = ss.helper.getStateAsQueryString(
                            s.getQueryOptions(s.action.VALIDATE, getFilters(ss.category)));
                                
                        $location.replace();
                        $location.search(newqs);
                        
                    });
                                                         
                }
                
            });
            
            /**
             * Returns a configuration object 
             * for retrieving and setting query parameters
             */
            s.getQueryOptions = function(action, moreFilters) { //$log.debug('getQueryOptions');
                
                var res = {
                    filters: moreFilters, 
                    prefix: ss.config.ALGOLIA_PREFIX,
                    moreAttributes: {
                        location_name: gs.search.location
                    }
                };
                
                var ordering = ss.getOrdering();
                
                if (ordering){
                    res.moreAttributes.order_by = ordering;    
                }
                
                if (action){
                    res.moreAttributes.action = action;
                }
                
                return res;
                
            };
            
            $rootScope.$on('render', function(e, result, state) { //$log.debug('renderLocation');
                
                $timeout(function(){
                
                    var newqs = ss.helper.getStateAsQueryString(s.getQueryOptions(s.action.RENDER));
                    $location.search(newqs);
                    
                    ga('send', 'pageview', $location.absUrl());
                
                }, 0, false);
                 
            });
            
            return s;
                    
        }).catch(function(){
            
            $log.error("Failed to init SearchLocationService");
            
        });;
        
    }]);
    
    
    /**
     * Manages maps and geocoding, 
     * stores current geogaraphical location
     */
    EloueWidgetsApp.factory('GeoService', 
    ["$rootScope", "$location", "$q", "uiGmapGoogleMapApi", 
    "UtilsService", "SearchService", "$log",
    function($rootScope, $location, $q, uiGmapGoogleMapApi, 
    UtilsService, SearchService, $log){
        
        return $q.all({
            ss: SearchService,
            maps: uiGmapGoogleMapApi
        }).then(function(services){
            
            var maps = services.maps, ss = services.ss;
            
            var s = {
                
                maps: maps,
                
                geoc: new maps.Geocoder(),
                
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
                            center: gmapToGeoJson(place.geometry.location),
                            place: place
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
                // $rootScope.$broadcast("place_changed", s);
                return s;
            }).finally(function(){
                NProgress.move(0.3);   
            });
        
        }).catch(function(){
            
            $log.error("Failed to init GeoService");
            
        });
            
    }]);
    
    
    /**
     * A base for all filter controllers.
     * Declares some of the common methods used by
     * filters.
     */
    var EloueFilterController = 
    ["$q", "$scope", "$rootScope", '$attrs', '$filter', 
    '$timeout', '$log', 'SearchService', 'SearchLocationService',
    function ($q, $scope, $rootScope, $attrs, $filter, 
    $timeout, $log, SearchService, SearchLocationService) {
        
        var vm = this;
        
        vm.apply = function(arg){
            $scope.$apply(arg);
        }
        
        // Filter model
        vm.value = $scope.value();
        // Default values 
        vm.defaults = $scope.defaults();
        // Algolia attribute name
        vm.attrName = $attrs.attrName;
        
        vm.apply = function(arg){
            $scope.$apply(arg);
        };

        // Called after each Algolia response to set the vm.value
        vm.render = function(e, result, state){};
        
        // Set some common values on the controller, and call
        // render. This is deferred to avoid big long frames
        vm.renderListener = $scope.$on('render', function(e, result, state){
            $timeout(function(){
                vm.empty = !result.nbHits;
                vm.resultCount = result.nbHits;
                vm.results = result.hits;
                vm.render(e, result, state);
                $scope.$digest();
            }, 0, false)
            .finally(NProgress.advance);
        });
        
        // Count in progress bar
        NProgress.register();
        
        // Called when a filter has changed
        // Must trigger a request to Algolia
        // vm.refine = vm.search;
        
        // Check if filter can be displayed
        vm.ready = function(){ 
            return false; 
        };
        
        // Keyboard event dispatcher
        // for filter hotkeys
        vm.onKeyup = function($event){
            if ($event.which in vm.hotkeys){
                vm.hotkeys[$event.which]();
            }
        };
        
        // Hotkey table
        vm.hotkeys = {};
        vm.hotkeys[KEY_ESC] = function(){
            vm.reset();
        };
        
        vm.filterControllerSetup = $q.all({
            sls:SearchLocationService,
            ss:SearchService
        }).then(function(services){
            
            var sls = services.sls, ss = services.ss;
            
            // Sends a search request
            vm.search = function(){
                ss.setOrdering("");
                ss.page = 0;
                ss.search();
            };
            
            // Condition to display the reset button
            vm.clean = function(){
                return !ss.helper.hasRefinements(vm.attrName);
            };
            
            // Called when reset button is pressed
            vm.reset = function(){
                ss.helper.clearRefinements(vm.attrName);
                vm.search();
            };
            
            return services;
            
        });
        

    }];
    
    
    EloueWidgetsApp.directive('starRating', function(){
        return {
            scope:false,
            restrict:"E",
            link: function(scope, element, attrs){
                scope.$watch(attrs.value, function(value){
                    var html = "";
                    for (var i=0; i<5; i++){
                        html += (i==parseInt(value)-1 ? 
                            "<span class='flaticon solid star-2 current-rate'></span>":
                            "<span class='flaticon solid star-2'></span>");
                    }
                    element.html(html);
                });
            }
        };
    });
    
    
    EloueWidgetsApp.directive('eloueFilter', 
    ['$filter', '$log', 
    function($filter, $log){
        return {
            restrict: 'AE',
            scope:{
                value:"&",
                defaults:"&",
                helper:"&"
            },
            transclude: true,
            controller: EloueFilterController,
            controllerAs: "vm",
            link: function(scope, element, attrs, vm, transclude){
                transclude(scope, function(clone, scope){
                    element.append(clone);
                });                
            }
        }    
    }]);
    
    
    /**
     * Provides the header for aside titles 
     * with filter name and reset button.
     * 
     * Modifies default transclude behavior by creating an isolate scope 
     * and providing it to the transclude function instead of the parent scope. 
     */
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
    
    
    /**
     * Same as eloueFilterWrapper but for text fields
     */
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
    
    /**
     * A slider filter. wrapper for rzSlider.
     * Provides conversion between metric and local units
     */
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
    
    /**
     * Price slider
     */
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
    
    /**
     * Distance slider
     */
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
                        // vm.setValue(gs.search.defaults, 'defaults');
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
    
    
    /**
     * Professional/private renter filter
     */
    EloueWidgetsApp.directive('elouePropart',  
    ['SearchService', '$log', '$rootScope',
    function(SearchService, $log, $rootScope){
        return {
            restrict: 'A',
            'require': 'eloueFilter',
            link: function($scope, $element, $attrs, vm){
                
                vm.filterControllerSetup.then(function(services){
                    
                    var ss = services.ss;

                    vm.render = function(e, result, state){ //$log.debug('renderRenterTypes');
                        var facetResult = result.getFacetByName("pro_owner");
                        if (!facetResult) {
                            vm.value.pro_count = 
                            vm.value.part_count = 
                            vm.value.count = 
                            vm.value.total_count = 0;
                            return;
                        }
                        vm.value.count = result.nbHits;
                        vm.value.pro_count = ('true' in facetResult.data ? 
                                                facetResult.data.true : 0);
                        vm.value.part_count = ('false' in facetResult.data ? 
                                                facetResult.data.false : 0);
                        vm.value.total_count = vm.value.pro_count + vm.value.part_count;
                        vm.value.pro = state.isDisjunctiveFacetRefined("pro_owner", true);
                        vm.value.part = state.isDisjunctiveFacetRefined("pro_owner", false);
                        vm.value.onlyProsAvail = vm.value.pro_count && !vm.value.part_count;
                        vm.value.onlyPartsAvail = !vm.value.pro_count && vm.value.part_count;
                        vm.value.bothAvail = vm.value.pro_count && vm.value.part_count;
                    };
                    
                    vm.refineRenterPart = function(){ //$log.debug('refineRenterPart');
                        if (!vm.value.part_count || vm.value.part){
                            return;
                        }
                        ss.helper.removeDisjunctiveFacetRefinement("pro_owner");
                        ss.helper.addDisjunctiveFacetRefinement("pro_owner", false);
                        vm.search();
                    };
                    
                    vm.refineRenterPro = function(){ //$log.debug('refineRenterPro');
                        if (!vm.value.pro_count || vm.value.pro){
                            return;
                        }
                        ss.helper.removeDisjunctiveFacetRefinement("pro_owner");
                        ss.helper.addDisjunctiveFacetRefinement("pro_owner", true);                        
                        vm.search();
                    };
                    
                    vm.resetAll = function(){
                        $rootScope.$broadcast('reset');
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
    
    
    /**
     * Search query text field
     */
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
                            ss.search(true);
                        }, vm.debounceDelay);
                    };
                                 
                    vm.clean = function(){
                        return !(ss.helper.state.query || vm.value);
                    };
                    
                    vm.reset = function() {
                        vm.value = vm.default;
                        $element.children('input')[0].focus();
                        ss.helper.setQuery(vm.default);
                        ss.search();
                    };
                            
                });
                
                vm.onFocus = function(){
                    vm.focus = true;    
                };
                
                vm.onBlur = function(){
                    vm.focus = false;
                };
                
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

    /**
     * Geographical location field. 
     * Wraps google places autocomplete.
     */
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
                    
                    vm.value = gs.search.location;

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

    /**
     * Category tree filter
     */
    EloueWidgetsApp.directive('eloueCategories',  
    ['SearchService', '$rootScope', '$log', 
    function(SearchService, $rootScope, $log){
        return {
            restrict: 'A',
            'require': 'eloueFilterWrapper',
            link: function ($scope, $element, $attrs, vm) {
                
                vm.filterControllerSetup.then(function(services){

                    var ss = services.ss;

                    vm.attrName = categoryAttributeName();
                    vm.categoryName = categoryName;
                    
                    vm.refine = function(path) { //$log.debug('refineCategory');

                        vm.value.algolia_category_path = path;
                        if (!vm.value.algolia_category_path){
                            ss.helper.clearRefinements(vm.attrName);

                        } else {
                            ss.helper.toggleRefinement(vm.attrName, vm.value.algolia_category_path);
                        }
                        
                        if (ss.helper.state.isHierarchicalFacetRefined(vm.attrName)){
                            ss.updateCategoryFromPath(
                                ss.helper.state.hierarchicalFacetsRefinements[vm.attrName][0])
                            .finally(function(){
                                NProgress.move(0.5);
                            });
                        }
                        
                        // $scope.clearPropertyRefinements();
                        vm.search();
                    };
                                
                    vm.render = function(e, result, state){
                        
                        vm.empty = !result.nbHits;
                        vm.resultCount = result.nbHits;
                        vm.results = result.hits;

                        vm.value = result.getFacetByName(vm.attrName);
                        
                    };
                    
                    var superClean = vm.clean;
                    
                    if (ss.defaults.category) {
                        vm.clean = function(){
                            return !superClean() && 
                                (ss.helper.state.hierarchicalFacetsRefinements[vm.attrName][0] ==
                                    ss.defaults.category.algolia_path);
                        };
                    } else {
                        vm.clean = function(){
                            return superClean() || !vm.value;
                        };   
                    }
                    
                    vm.ready = function(){
                        return true;
                    };
                    
                    vm.reset = function(){
                        ss.helper.clearRefinements(vm.attrName);
                        if (ss.defaults.category) {
                            ss.helper.toggleRefinement(vm.attrName, 
                                ss.defaults.category.algolia_path);
                        }
                        ss.setCategory(ss.defaults.category);

                        vm.leaf_category = "";
                        vm.search(); 
                    };
                    
                     
                });
                
            }
        };
    }]);    
    
    /**
     * Map
     * This is not a filter, but it uses eloueFilterWrapper to
     * show a header and respond to render events 
     */
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
                        zoom: UtilsService.zoom(gs.search.range.max),
                        center: gs.search.center,
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
    
   
    /**
     * Updates dynamic properties when a category changes
     */
    EloueWidgetsApp.controller("DynamicPropertiesController", 
    ["$scope", "SearchService", "$log",
    function($scope, SearchService, $log) {
        
        $scope.properties = [];
        
        $scope.setCategory = function(category){
            $scope.properties = category ? category.properties : [];
        };
            
        $scope.$on('categoryChanged', function(e, category){ //$log.debug(category);
            $scope.setCategory(category);
        });
        
        SearchService.then(function(ss){
            $scope.setCategory(ss.category);
        });
        
    }]);
    
    /**
     * A dynamic property built from a model provided by
     * a category. Supports only text value dropdown 
     * for the moment
     */
    EloueWidgetsApp.directive('eloueDynamicProperty', 
    ["SearchService",
    function(SearchService){
        return {
            restrict: 'A',
            'require': ['eloueFilterWrapper', 'ngModel'],
            link: function (scope, element, attrs, ctrls) {
                                  
                var vm = ctrls[0], ngModel = ctrls[1];
            
                ngModel.$render = function(){
                    var proto = ngModel.$viewValue;
                    if (proto) {
                        vm.attrName = proto.attr_name;
                        vm.label = proto.name;
                        vm.value = vm.defaults = proto.default;
                        vm.choices = proto.choices;
                        vm.prop_id = proto.id;
                    }
                };
                
                vm.ready = function(){
                    return true;
                };
                
                vm.filterControllerSetup.then(function(services){
              
                    var ss = services.ss;
  
                    vm.clean = function(){
                        return vm.value == vm.defaults;
                    };
                    
                    vm.refine = function(){
                        
                        if (ss.helper.state.isFacetRefined(vm.attrName)){
                            ss.helper.removeFacetRefinement(vm.attrName);
                        }
                        // FIXME a hack - shoud determine this otherwise
                        if (vm.value !== vm.choices[0]){
                            ss.helper.addFacetRefinement(
                                vm.attrName, vm.value);   
                        }
                        ss.search();
                    };
                    
                    vm.render = function(e, result, state){
                        if ((state.facets.indexOf(vm.attrName)>=0) && state.isFacetRefined(vm.attrName)){
                            vm.value = state.getConjunctiveRefinements(vm.attrName)[0];
                        } else {
                            vm.value = vm.defaults;
                        }
                    }; 
                                       
                });
                
          }
        };
    }]);
    
    
    /**
     * Pagination
     */
    EloueWidgetsApp.directive('elouePagination', 
    ['$rootScope', '$window', '$timeout', 'SearchService',
    function($rootScope, $window, $timeout, SearchService){
        
        return {
            scope:{},
            restrict:'E',
            templateUrl:'_pagination.html',
            link:function($scope, $element, $attrs){
                
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
                        $timeout(function(){
                            $scope.ui_pristine = false;//TODO ss.ui_pristine();
                            $scope.pages_count = result.nbPages;
                            $scope.result_count = result.nbHits;
                            $scope.page = result.page;
                            $scope.makePaginationModel(result.nbPages, result.page);
                            NProgress.advance(function(){
                                $scope.$digest();
                            });
                        }, 0, false);
                    });    
                    
                    
                });
                
            }
        };
        
    }]);
    
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
                
                /*
                 * Pagination & ordering 
                 */
                
                $scope.ordering = "";
                $scope.setOrdering = function(ordering){ //$log.debug('setOrdering');
                    ss.setOrdering(ordering);
                    ss.search();
                };
                
                $scope.clearRefinements = function(){
                    ss.reset();
                    ss.helper.setQuery("");
                    ss.setCategory(null);
                    gs.setPlace(gs.defaults.place);
                    ss.setPlace(gs.defaults);
                    ss.search();
                };                
                
                $scope.$on('reset', $scope.clearRefinements);
                
                $scope.$on('render',  function(e, result, state) { //$log.debug('renderOrdering');
                    $timeout(function(){
                        $scope.enableDistance = !gs.isLocationDefault();
                        $scope.ordering = ss.getOrdering();
                        $scope.location = gs.location;
                        $scope.result_count = result.nbHits;
                        $scope.query = result.query;
                        $scope.product_list = result.hits;
                        $scope.results_per_page = result.hitsPerPage;
                        $scope.ui_pristine = false;
                        // TODO refactor
                        var facetResult = result.getFacetByName("pro_owner");
                        if (facetResult){
                            $scope.pro_count = ('true' in facetResult.data ? 
                                                    facetResult.data.true : 0);
                            $scope.part_count = ('false' in facetResult.data ? 
                                                    facetResult.data.false : 0);    
                        } else {
                            $scope.part_count = $scope.pro_count = 0;
                        }
                        if (state.isDisjunctiveFacetRefined("pro_owner", true)){
                            $scope.owner_type = "pro";        
                        } else if (state.isDisjunctiveFacetRefined("pro_owner", false)){
                            $scope.owner_type = "part";
                        } else if (!state.isDisjunctiveFacetRefined("pro_owner")) {
                            $scope.owner_type = null;
                        };
                        $scope.$digest();
                    }, 0, false);
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
                
                $scope.activateLayoutSwitcher();

                if (ss.category && (!ss.defaults.category || ss.category.algolia_path !=
                        ss.defaults.category.algolia_path)){
                    ss.helper.toggleRefinement(categoryAttributeName(), ss.category.algolia_path);
                }
                ss.setPlace(gs.search);
                
                ss.search(true);    
                
            });
                    
        }]);
    
});
