define(["eloue/app",
        "eloue/controllers/HomePageCtrl",
        "eloue/controllers/ProductListCtrl",
        "eloue/controllers/product_details/BookingCtrl",
        "eloue/controllers/product_details/ProductDetailsCtrl",
        "eloue/controllers/product_details/CalendarCtrl",
        "eloue/controllers/publish_item/PublishAdCtrl",
        "../../common/eloue/controllers/AuthCtrl",
        "../../common/eloue/controllers/LoginCtrl",
        "../../common/eloue/controllers/RegisterCtrl",
        "../../common/eloue/controllers/ResetPasswordCtrl",
        "../../common/eloue/directives/Chosen",
        "../../common/eloue/directives/DashboardRedirect",
        "../../common/eloue/directives/Datepicker",
        "../../common/eloue/directives/DatepickerMonth",
        "../../common/eloue/directives/ExtendedDatepicker",
        "../../common/eloue/directives/FormFieldErrorManager",
        "../../common/eloue/directives/FormFieldMessage",
        "../../common/eloue/directives/FormMessage",
        "../../common/eloue/directives/LoginForm",
        "../../common/eloue/directives/PasswordMatch",
        "../../common/eloue/directives/RegistrationForm",
        "../../common/eloue/directives/ResetPasswordForm",
        "../../common/eloue/directives/ScrollBottom",
        "../../common/eloue/directives/ZipcodeValidator",
        "../../common/eloue/interceptors/ErrorHandlerInterceptor"],
    function (EloueApp) {
        "use strict";

        /**
         * Routing configuration for app.
         */
        EloueApp.config([
            "$httpProvider",
            function ($httpProvider) {
                // push function to the responseInterceptors which will intercept
                // the http responses of the whole application
                $httpProvider.interceptors.push("ErrorHandlerInterceptor");
                // use the HTML5 History API
//                $locationProvider.html5Mode(true);
            }
        ]);

        EloueApp.run(["$http", "AuthService", function ($http, AuthService) {
            var userToken = AuthService.getUserToken(),
                csrftoken = AuthService.getCSRFToken();
            $http.defaults.useXDomain = true;
            delete $http.defaults.headers.common["X-Requested-With"];
            if (userToken && userToken.length > 0) {
                $http.defaults.headers.common.authorization = "Bearer " + userToken;
            }
            if (csrftoken && csrftoken.length > 0) {
                $http.defaults.headers.common["X-CSRFToken"] = csrftoken;
            }
        }]);
    });
