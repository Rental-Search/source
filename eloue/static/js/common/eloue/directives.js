"use strict";
define(["../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Datepicker directive.
     */
    EloueCommon.directive("eloueDatepicker", function () {
        return {
            restrict: "A",
            replace: true,
            require: "?ngModel",
            transclude: true,
            link: function (scope, element, attrs, ngModel) {
                if (!ngModel) return;
                element.datepicker({
                    language: "fr",
                    autoclose: true,
                    todayHighlight: true,
                    startDate: Date.today()
                });
            }
        };
    });

    EloueCommon.directive("eloueChosen", ["$timeout", function($timeout) {
        return {
            restrict: "A",
            link: function (scope, element, attrs) {

                scope.$watch(attrs["chosen"], function () {
                    element.trigger("chosen:updated");
                });

                scope.$watch(attrs["ngModel"], function() {
                    element.trigger("chosen:updated");
                });

                scope.$watch(attrs["opts"], function() {
                    $timeout(function() {
                        element.trigger("chosen:updated");
                    }, 300);
                });

                element.chosen();
            }
        };
    }]);

    EloueCommon.directive("eloueDatepickerMonth", function () {
        return {
            restrict: "A",
            replace: true,
            require: "?ngModel",
            transclude: true,
            link: function (scope, element, attrs, ngModel) {
                if (!ngModel) return;
                element.datepicker({
                    language: "fr",
                    format: "mm/yy",
                    viewMode: "months",
                    minViewMode: "months",
                    autoclose: true,
                    startDate: Date.today()
                });
            }
        };
    });

    /**
     * Directive to display registration form.
     */
    EloueCommon.directive("eloueRegistrationForm", ["Path", function (Path) {
        return {
            restrict: "E",
            templateUrl: Path.templatePrefix + "partials/homepage/registration-form.html",
            scope: {},
            controller: "RegisterCtrl"
        };
    }]);

    /**
     * Directive to display login form.
     */
    EloueCommon.directive("eloueLoginForm", ["Path", function (Path) {
        return {
            restrict: "E",
            templateUrl: Path.templatePrefix + "partials/homepage/login-form.html",
            scope: {},
            controller: "LoginCtrl"
        };
    }]);

    /**
     * Directive to validate password confirmation.
     */
    EloueCommon.directive("elouePasswordMatch", ["$parse", function ($parse) {
        return {
            restrict: "A",
            require: "ngModel",
            link: function (scope, element, attrs, ngModel) {
                ngModel.$parsers.unshift(function (viewValue, $scope) {
                    var noMatch = viewValue != scope.registrationForm.password.$viewValue;
                    ngModel.$setValidity("noMatch", !noMatch);
                    return viewValue;
                })
            }
        }
    }]);

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
                                if (scope.hasNextPage) {
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
                            }
                        );
                    };

                    $rootScope.$on("startLoading", function (event, args) {
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

                    $rootScope.$on("hideLoading", function () {
                        loadingWidget.hide();
                    });
                    $rootScope.$on("showLoading", function () {
                        loadingWidget.show();
                    });
                }};
        }]);
});