define([
    '../../../common/eloue/commonApp',
    '../../../common/eloue/services/LazyLoader'
], function (EloueCommon) {
    'use strict';
    /**
     * Lazy loading list components.
     *
     * Additional config can be provided:
     * resultField: Custom field name which contains result array. 'list' by default,
     * inverse: True to inverse lazy load and show spinner and 'load more' button on the top of the list,
     * loadingTarget: Set any string to make broadcast events to affect only specified target.
     */
    EloueCommon.directive('eloueLazyLoad', ['$injector', '$window', '$document', '$timeout', '$rootScope', '$filter', 'LazyLoader',
        function ($injector, $window, $document, $timeout, $rootScope, $filter, LazyLoader) {

            var appendAnimations = function () {
                var style = $document[0].createElement('style');
                style.innerHTML = '@-webkit-keyframes spin {\n' +
                '\t0%{-webkit-transform: rotate(0deg);}\n' +
                '\t100%{-webkit-transform: rotate(360deg);}\n' +
                '}\n' +
                '@keyframes spin{\n' +
                '\t0%{transform: rotate(0deg);}\n' +
                '\t100%{transform: rotate(360deg);}\n' +
                '}';
                $document[0].head.appendChild(style);
            }, makeSpinner = function (el, color) {
                el.css({
                    WebkitBoxSizing: 'border-box',
                    boxSizing: 'border-box',
                    display: 'block',
                    width: '43px',
                    height: '43px',
                    margin: '20px auto',
                    borderWidth: '8px',
                    borderStyle: 'solid',
                    borderColor: color,
                    borderRadius: '22px',
                    animation: 'spin 0.8s linear infinite',
                    WebkitAnimation: 'spin 0.8s linear infinite'
                });
                return el;
            };

            return {
                restrict: 'A',
                require: '?ngModel',
                scope: {
                    lazyData: '=',
                    lazyDataProvider: '@',
                    lazyLoadMethod: '@',
                    config: '=lazyLoadConfig'
                },
                link: function (scope, element, attrs, ngModel) {
                    var winEl = angular.element($window),
                        win = winEl[0],
                        loadingWidget,
                        loadMoreButton,
                        lazyLoader = LazyLoader,
                        dataProvider = $injector.get(scope.lazyDataProvider),
                        lazyLoad,
                        loadingWidgetHtml = '<div class=\'col-md-12 loading\' style=\'background-image: none\'>' +
                            '<div class=\'loading-widget\'></div>' +
                            '</div>',
                        loadMoreButtonHtml = '<div class=\'col-md-12 text-center load-more-button\'>' +
                            '<a class=\'text text-success text-underline-hover\'>' + $filter('translate')('loadMore') + '</a>' +
                            '</div>';

                    scope.page = 1;
                    scope.hasNextPage = true;
                    scope.isLoading = false;

                    // Init events names.
                    var startLoadingEventName = 'startLoading';
                    var showLoadingEventName = 'showLoading';
                    var hideLoadingEventName = 'hideLoading';

                    // If target name is provided, set unique event names.
                    if (scope.config && scope.config.loadingTarget) {
                        startLoadingEventName += scope.config.loadingTarget;
                        showLoadingEventName += scope.config.loadingTarget;
                        hideLoadingEventName += scope.config.loadingTarget;
                    }


                    if (scope.config && scope.config.inverse) {
                        // If list is reversed, add load more widget and spinner on the top.
                        element.prepend(loadingWidgetHtml);
                        element.prepend(loadMoreButtonHtml);
                    }
                    else {
                        // Or to the bottom orherwise.
                        element.append(loadingWidgetHtml);
                        element.append(loadMoreButtonHtml);
                    }

                    loadingWidget = angular.element(element[0].querySelector('.loading-widget'));
                    loadMoreButton = angular.element(element[0].querySelector('.load-more-button'));

                    // If button placed on the top, remove bottom border and margin.
                    if (scope.config && scope.config.inverse) {
                        loadMoreButton.css({
                            'border-bottom': '0',
                            'margin-bottom': '0'
                        })
                    }

                    // Hide load more button by default.
                    loadMoreButton.hide();

                    // Load next page on load more button click.
                    loadMoreButton.on('click', function () {
                        scope.shouldReloadList = false;
                        lazyLoad();
                    });

                    element.mCustomScrollbar({
                        scrollInertia: '100',
                        autoHideScrollbar: true,
                        theme: 'dark-thin',
                        advanced: {
                            updateOnContentResize: true,
                            autoScrollOnFocus: false
                        },
                        callbacks: {
                            onTotalScroll: function () {
                                if (scope.hasNextPage && !scope.isLoading) {
                                    if (scope.config && scope.config.inverse) {
                                        return;
                                    }
                                    win.requestAnimationFrame(function () {
                                        scope.shouldReloadList = false;
                                        scope.$apply(function () {
                                            lazyLoad();
                                        });
                                    });
                                }
                            }
                        }
                    });
                    appendAnimations();
                    makeSpinner(loadingWidget, 'transparent rgb(44, 44, 44) rgb(44, 44, 44) rgb(44, 44, 44)');

                    lazyLoad = function () {
                        scope.isLoading = true;
                        var args = scope.lazyLoadArgs.slice(0);
                        args.push(scope.page);
                        lazyLoader.configure({
                            data: scope.lazyData,
                            fetchData: dataProvider[scope.lazyLoadMethod],
                            range: scope.lazyRange,
                            args: args,
                            showLoadingEventName: showLoadingEventName,
                            hideLoadingEventName: hideLoadingEventName
                        });

                        lazyLoader.load()
                            .then(function (data) {
                                if (!data.next) {
                                    scope.hasNextPage = false;
                                } else {
                                    scope.page += 1;
                                }

                                // Get result array.
                                var dataList = scope.config && scope.config.resultField ? data[scope.config.resultField] : data.list;

                                if (!scope.shouldReloadList) {
                                    angular.forEach(Object.keys(dataList), function (key) {
                                        scope.lazyData.push(dataList[key]);
                                    });
                                } else {
                                    scope.lazyData = dataList;
                                }
                                scope.isLoading = false;
                                if (!scope.hasNextPage) {
                                    loadMoreButton.hide();
                                }
                            }, function (error) {
                                loadMoreButton.show();
                            });
                    };

                    scope.$on(startLoadingEventName, function (event, args) {
                        if (args.shouldReloadList) {
                            scope.page = 1;
                            scope.shouldReloadList = true;
                            scope.hasNextPage = true;
                        } else {
                            scope.shouldReloadList = false;
                        }
                        scope.lazyLoadArgs = args.parameters;
                        lazyLoad();
                    });

                    scope.$on(hideLoadingEventName, function () {
                        $rootScope.routeChangeInProgress = false;
                        loadingWidget.hide();
                        loadMoreButton.show();
                    });
                    scope.$on(showLoadingEventName, function () {
                        $rootScope.routeChangeInProgress = true;
                        loadingWidget.show();
                        loadMoreButton.hide();
                    });
                }
            };
        }]);
});
