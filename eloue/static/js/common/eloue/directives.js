"use strict";
define(["../../common/eloue/commonApp",
    "datejs",
    "chosen",
    "bootstrap-datepicker",
    "bootstrap-datepicker-fr",
    "jquery-mousewheel",
    "custom-scrollbar"], function (EloueCommon) {
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

    /**
     * Directive allows to set "eloue-err-src" attribute on <img> tag to be applied if calling path defined in "src" returns 404 error.
     */
    EloueCommon.directive("eloueErrSrc", function () {
        return {
            restrict: "A",
            link: function (scope, element, attrs) {
                element.bind("error", function () {
                    if (attrs.src != attrs.errSrc) {
                        attrs.$set("src", attrs.errSrc);
                    }
                });
            }
        }
    });

    EloueCommon.directive("eloueChosen", ["$timeout", function ($timeout) {
        return {
            restrict: "A",
            link: function (scope, element, attrs) {

                scope.$watch(attrs["chosen"], function () {
                    element.trigger("chosen:updated");
                });

                scope.$watch(attrs["ngModel"], function () {
                    element.trigger("chosen:updated");
                });

                scope.$watch(attrs["opts"], function () {
                    $timeout(function () {
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
     * Directive to display reset password form.
     */
    EloueCommon.directive("eloueResetPasswordForm", ["Path", function (Path) {
        return {
            restrict: "E",
            templateUrl: Path.templatePrefix + "partials/homepage/reset-password-form.html",
            scope: {},
            controller: "ResetPasswordCtrl"
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
                }};
        }]);

    /**
     * Directive to show global error message for form.
     * If it's have not message set ng-hide to container.
     */
    EloueCommon.directive("eloueFormMessage", ["$animate","ServerValidationService", function ( $animate, ServerValidationService) {
        return {
            restrict: "A",
            scope:true,
            link: function (scope, element, attrs) {
                var formTag=attrs.formTag;
                if(!!formTag){
                   scope.$watchCollection(function(){
                      return ServerValidationService.getFormErrorMessage(formTag);
                   },function(value){
                       if(!!value) {
                           $animate['removeClass'](element, 'ng-hide');
                           scope.message = value.message;
                           scope.description = value.description;
                       } else{
                           $animate['addClass'](element, 'ng-hide');
                       }
                   });
                }
            }
        }
    }]);

    /**
     * Directive to show field error message for form's field.
     * If it's have not message set ng-hide to container.
     */
    EloueCommon.directive("eloueFormFieldMessage", ["$animate", "ServerValidationService", function ($animate, ServerValidationService) {
        return {
            restrict: "A",
            scope:true,
            link: function (scope, element, attrs) {
                var formTag, fieldName;
                formTag=attrs.formTag;
                fieldName=attrs.fieldName;
                if(!!formTag && !!fieldName){
                    scope.$watch(function(){
                        return ServerValidationService.getFieldError(formTag, fieldName);
                    },function(value){
                        if(!!value) {
                            $animate['removeClass'](element, 'ng-hide');
                            scope.value = value[0];
                        } else{
                            $animate['addClass'](element, 'ng-hide');
                        }
                    });
                }
            }
        }
    }]);


    /**
     * When the validation error occurred this directive try to find all field with errors by name and add error block.
     * If block contain "eloueFormFieldMessage" with error field name, directive dose not add error block.
     */
    EloueCommon.directive("eloueFormFieldErrorManager", ["$animate", "ServerValidationService", function ($animate, ServerValidationService) {
        var className = "server-validation-error";
        function prepareErrorElement(message){
            return "<span class='text-danger " + className + "'>"+message+"</span>"
        }
        return {
            restrict: "AE",
            link: function (scope, element, attrs) {
                var formTag = attrs.formTag;
                   if(!!formTag) {
                       scope.$watch(function () {
                           return ServerValidationService.getErrors(formTag);
                       }, function (value) {
                           var el = element;
                           el.find("." + className).remove();
                           if(!!value){
                               angular.forEach(value.fields, function(value, key) {
                                   var checkItem, input;
                                   checkItem = el.find("[field-name='" + key + "']");
                                   if(checkItem.length === 0) {
                                       input = el.find("[name='" + key + "']");
                                       input.parent().append(prepareErrorElement(value));
                                   }
                               });
                           }
                       });
                   }
            }
        }
    }]);

});