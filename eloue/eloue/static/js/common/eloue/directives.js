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
                element.datepicker();
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
                    lazyDataCollectionKey: "@",
                    lazyDataService: "@",
                    lazyFetchMethod: "@",
                    lazyRange: "@",
                    lazyDataKeys: "=",
                    lazyStartDelay: "@",
                    lazyAppendDelay: "@",
                    lazySpinnerColor: "@"
                },
                link: function (scope, element, attrs, ngModel) {

                    element.append(
                            "<div class=\"col-md-12 loading\" ng-hide=\"spinner.hide\">" +
                            "<div class=\"loading-widget\"></div>" +
                            "</div>"
                    );

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
                                loading = true;
                                win.requestAnimationFrame(function () {
                                    scope.$apply(function () {
                                        lazyLoad();
                                    });
                                });
                            }
                        }
                    });

                    var winEl = angular.element($window),
                        win = winEl[0],
                        loadingWidget = angular.element(document.querySelector(".loading-widget")),
                        lazyLoader = LazyLoader,
                        dataService = $injector.get(scope.lazyDataService),
                        hasRun = false,
                        loading = true;
                    appendAnimations();
                    makeSpinner(loadingWidget, "transparent rgb(44, 44, 44) rgb(44, 44, 44) rgb(44, 44, 44)");
                    scope.spinner = { hide: false };

                    var lazyLoad = function () {
                        lazyLoader.configure({
                            data: scope.lazyData,
                            collectionKey: scope.lazyDataCollectionKey,
                            fetchData: dataService[scope.lazyFetchMethod],
                            range: scope.lazyRange,
                            dataKeys: scope.lazyDataKeys
                        });

                        lazyLoader.load()
                            .then(
                            function (data) {
                                if (!hasRun) {
                                    angular.forEach(Object.keys(data), function (key) {
                                        scope.lazyData[key] = data[key];
                                    });
                                } else {
                                    scope.lazyData[scope.lazyDataCollectionKey] = data[scope.lazyDataCollectionKey];
                                }
                                loading = false;
                            }
                        );
                    };

                    $rootScope.$on("hideLoading", function () {
                        scope.spinner.hide = true;
                    });
                    $rootScope.$on("showLoading", function () {
                        scope.spinner.hide = false;
                    });

                    lazyLoad();
                }};
        }]);
});