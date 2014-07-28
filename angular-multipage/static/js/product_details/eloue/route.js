
define(["eloue/app",
        "eloue/controllers/ProductDetailsCtrl",
        "eloue/directives/ProductDetailsBookingDirective",
        "eloue/directives/BookingModalDirective",
        "eloue/directives/MessageModalDirective",
        "eloue/directives/PhoneModalDirective",
        "eloue/directives/ProductDetailsSmallDirective",
        "eloue/directives/validation/DatetimepickerDirective"],
    function (EloueApp) {

        "use strict";
        EloueApp.run(["$rootScope", "$location", "$route", "$http", function ($rootScope, $location, $route, $http) {
            var userToken = "";
            var name = "user_token=";
            var ca = document.cookie.split(';');
            for (var i = 0; i < ca.length; i++) {
                var c = ca[i];
                while (c.charAt(0) == ' ') c = c.substring(1);
                if (c.indexOf(name) != -1) {
                    userToken = c.substring(name.length, c.length);
                }
            }
            $http.defaults.useXDomain = true;
            delete $http.defaults.headers.common['X-Requested-With'];
            $http.defaults.headers.common.authorization = "Bearer " + userToken;
        }]);
    });