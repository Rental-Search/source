define(["eloue/app",
        "eloue/modules/booking/controllers/ProductDetailsCtrl",
        "eloue/modules/booking/controllers/PublishAdCtrl",
        "../../common/eloue/services", "../../common/eloue/controllers", "../../common/eloue/directives", "../../common/eloue/interceptors"],
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
                $httpProvider.responseInterceptors.push("ErrorHandlerInterceptor");
                // use the HTML5 History API
//                $locationProvider.html5Mode(true);
            }
        ]);

        EloueApp.run(["$location", "$http", "AuthService", function ($location, $http, AuthService) {
            var userToken = AuthService.getCookie("user_token");
            $http.defaults.useXDomain = true;
            delete $http.defaults.headers.common['X-Requested-With'];
            if (userToken && userToken.length > 0) {
                $http.defaults.headers.common.authorization = "Bearer " + userToken;
            }
            var csrftoken = AuthService.getCookie('csrftoken');
            if (csrftoken && csrftoken.length > 0) {
                $http.defaults.headers.common["X-CSRFToken"] = csrftoken;
            }
        }]);
    });