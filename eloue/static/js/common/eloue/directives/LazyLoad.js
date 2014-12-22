"use strict";
define([
    "../../../common/eloue/commonApp",
    "../../../common/eloue/services/LazyLoader"
], function (EloueCommon) {
    /**
     * Lazy loading list components.
     */
    EloueCommon.directive("eloueLazyLoad", ["$injector", "$window", "$document", "$timeout", "$rootScope", "LazyLoader",
        function ($injector, $window, $document, $timeout, $rootScope, LazyLoader) {

            var appendAnimations = function () {
                var style = document.createElement("style");
                style.innerHTML = "@-webkit-keyframes spin {\n" +
                "\t0%{-webkit-transform: rotate(0deg);}\n" +
                "\t100%{-webkit-transform: rotate(360deg);}\n" +
                "}\n" +
                "@keyframes spin{\n" +
                "\t0%{transform: rotate(0deg);}\n" +
                "\t100%{transform: rotate(360deg);}\n" +
                "}";
                document.head.appendChild(style);
            };

            var makeSpinner = function (el, color) {
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
                    scope.page = 1;
                    scope.hasNextPage = true;
                    scope.isLoading = false;
                    element.append(
                        "<div class=\"col-md-12 loading\">" +
                        "<div class=\"loading-widget\"></div>" +
                        "</div>"
                    );

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

                    var winEl = angular.element($window),
                        win = winEl[0],
                        loadingWidget = angular.element(document.querySelector(".loading-widget")),
                        lazyLoader = LazyLoader,
                        dataProvider = $injector.get(scope.lazyDataProvider);
                    appendAnimations();
                    makeSpinner(loadingWidget, "transparent rgb(44, 44, 44) rgb(44, 44, 44) rgb(44, 44, 44)");

//                    dataProvider[scope.lazyLoadMethod].apply(null,scope.lazyLoadArgs);
                    var lazyLoad = function () {
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
                            .then(
                            function (data) {
                                if (!data.next) {
                                    scope.hasNextPage = false;
                                } else {
                                    scope.page++;
                                }
                                if (!scope.shouldReloadList) {
                                    angular.forEach(Object.keys(data.list), function (key) {
                                        scope.lazyData.push(data.list[key]);
                                    });
                                } else {
                                    scope.lazyData = data.list;
                                }
                                scope.isLoading = false;
                            }
                        );
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
                    });
                    scope.$on("showLoading", function () {
                        $rootScope.routeChangeInProgress = true;
                        loadingWidget.show();
                    });
                }
            };
        }]);
});
