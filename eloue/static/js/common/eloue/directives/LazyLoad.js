define([
    "../../../common/eloue/commonApp",
    "../../../common/eloue/services/LazyLoader"
], function (EloueCommon) {
    "use strict";
    /**
     * Lazy loading list components.
     */
    EloueCommon.directive("eloueLazyLoad", ["$injector", "$window", "$document", "$timeout", "$rootScope", "$filter", "LazyLoader",
        function ($injector, $window, $document, $timeout, $rootScope, $filter, LazyLoader) {

            var appendAnimations = function () {
                var style = $document[0].createElement("style");
                style.innerHTML = "@-webkit-keyframes spin {\n" +
                "\t0%{-webkit-transform: rotate(0deg);}\n" +
                "\t100%{-webkit-transform: rotate(360deg);}\n" +
                "}\n" +
                "@keyframes spin{\n" +
                "\t0%{transform: rotate(0deg);}\n" +
                "\t100%{transform: rotate(360deg);}\n" +
                "}";
                $document[0].head.appendChild(style);
            }, makeSpinner = function (el, color) {
                el.css({
                    WebkitBoxSizing: "border-box",
                    boxSizing: "border-box",
                    display: "block",
                    width: "43px",
                    height: "43px",
                    margin: "20px auto",
                    borderWidth: "8px",
                    borderStyle: "solid",
                    borderColor: color,
                    borderRadius: "22px",
                    animation: "spin 0.8s linear infinite",
                    WebkitAnimation: "spin 0.8s linear infinite"
                });
                return el;
            };

            return {
                restrict: "A",
                require: "?ngModel",
                scope: {
                    lazyData: "=",
                    lazyDataProvider: "@",
                    lazyLoadMethod: "@"
                },
                link: function (scope, element, attrs, ngModel) {
                    var winEl = angular.element($window),
                        win = winEl[0],
                        loadingWidget,
                        loadMoreButton,
                        lazyLoader = LazyLoader,
                        dataProvider = $injector.get(scope.lazyDataProvider),
                        lazyLoad;

                    scope.page = 1;
                    scope.hasNextPage = true;
                    scope.isLoading = false;
                    scope.loadMoreText = $filter('translate')('loadMore');

                    element.append(
                        "<div class=\"col-md-12 loading\" style=\"background-image: none\">" +
                        "<div class=\"loading-widget\"></div>" +
                        "</div>"
                    );

                    element.append(
                        "<div class=\"col-md-12 text-center load-more-button\">" +
                        "<a class=\"text text-success text-underline-hover\">" + scope.loadMoreText + "</a>" +
                        "</div>"
                    );

                    loadingWidget = angular.element($document[0].querySelector(".loading-widget"));
                    loadMoreButton = angular.element($document[0].querySelector(".load-more-button"));
                    loadMoreButton.on("click", function () {
                        lazyLoad();
                    });

                    element.mCustomScrollbar({
                        scrollInertia: "100",
                        autoHideScrollbar: true,
                        theme: "dark-thin",
                        advanced: {
                            updateOnContentResize: true,
                            autoScrollOnFocus: false
                        },
                        callbacks: {
                            onTotalScroll: function () {
                                if (scope.hasNextPage && !scope.isLoading) {
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
                    makeSpinner(loadingWidget, "transparent rgb(44, 44, 44) rgb(44, 44, 44) rgb(44, 44, 44)");

                    lazyLoad = function () {
                        scope.isLoading = true;
                        var args = scope.lazyLoadArgs.slice(0);
                        args.push(scope.page);
                        lazyLoader.configure({
                            data: scope.lazyData,
                            fetchData: dataProvider[scope.lazyLoadMethod],
                            range: scope.lazyRange,
                            args: args
                        });

                        lazyLoader.load()
                            .then(function (data) {
                                if (!data.next) {
                                    scope.hasNextPage = false;
                                } else {
                                    scope.page += 1;
                                }
                                if (!scope.shouldReloadList) {
                                    angular.forEach(Object.keys(data.list), function (key) {
                                        scope.lazyData.push(data.list[key]);
                                    });
                                } else {
                                    scope.lazyData = data.list;
                                }
                                scope.isLoading = false;
                                if (!scope.hasNextPage) {
                                    loadMoreButton.hide();
                                }
                            }, function (error) {
                                loadMoreButton.show();
                            });
                    };

                    scope.$on("startLoading", function (event, args) {
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

                    scope.$on("hideLoading", function () {
                        $rootScope.routeChangeInProgress = false;
                        loadingWidget.hide();
                        loadMoreButton.show();
                    });
                    scope.$on("showLoading", function () {
                        $rootScope.routeChangeInProgress = true;
                        loadingWidget.show();
                        loadMoreButton.hide();
                    });
                }
            };
        }]);
});
