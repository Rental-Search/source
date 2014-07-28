
define(["eloue/app", "eloue/services/AuthService",
        "eloue/controllers/LoginCtrl",
        "eloue/controllers/RegisterCtrl",
        "eloue/directives/LoginFormDirective",
        "eloue/directives/RegistrationFormDirective",
        "eloue/directives/validation/PasswordMatchDirective"],
    function (EloueApp) {

        "use strict";
        EloueApp.run(["$rootScope", "$location", "$route", "$http", "AuthService", function ($rootScope, $location, $route, $http, AuthService) {
            var userToken = AuthService.getCookie("user_token");
            $http.defaults.useXDomain = true;
            delete $http.defaults.headers.common['X-Requested-With'];
            $http.defaults.headers.common.authorization = "Bearer " + userToken;

            // Route change event listener
            $rootScope.$on("$locationChangeStart", function (event, next, current) {
                // Redirect not authenticated user
                var routes = $route.routes;
                for (var i in routes) {
                    if (next.indexOf(i) != -1) {
                        if (routes[i].secure && !AuthService.isLoggedIn()) {
                            $rootScope.$broadcast("redirectToLogin");
                            event.preventDefault();
                        }
                    }
                }
            });

            $rootScope.$on("redirectToLogin", function() {
                $location.path("/");
            });
        }]);
    });