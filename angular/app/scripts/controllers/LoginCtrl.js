define(["angular"], function (angular) {
    "use strict";

    angular.module("LoginModule", []).controller("LoginCtrl", ["$scope", "$cookieStore", function ($scope, $cookieStore) {
        $scope.credentials = {};

        $scope.login = function login() {
            console.log("In login");
            var userToken = $cookieStore.get("user_token");
            if (!userToken) {
                $.ajax({
                    url: "http://10.0.0.111:8000/oauth2/access_token/",
                    type: "POST",
                    data: {
                        client_id: "51bcafe59e484b028657",
                        client_secret: "132a8a395c140e29f15c4341758c59faa33e012b",
                        grant_type: "password",
                        username: $scope.credentials.username,
                        password: $scope.credentials.password
                    },
                    success: function (data) {
                        console.log(data.access_token);
                        $cookieStore.put("user_token", data.access_token);
                        $scope.authorize();
                    },
                    error: function (jqXHR) {
                        if (jqXHR.status == 400) {
                            window.alert("An error occured: " + jqXHR.responseJSON);
                        } else {
                            window.alert("An error occured!");
                        }
                    }
                });
            } else {
                $scope.authorize();
            }
        };

        $scope.authorize = function authorize() {
            var userToken = $cookieStore.get("user_token");
            if (userToken) {
                $.ajax({
                    url: "http://10.0.0.111:8000/api/2.0/users/",
                    type: "POST",
                    headers: {
                        Authorization: "Bearer " + userToken
                    },
                    data: {},
                    success: function (data) {
                        console.log(data);
                    },
                    error: function (jqXHR) {
                        if (jqXHR.status == 400) {
                            window.alert("An error occured: " + jqXHR.responseJSON);
                        } else {
                            window.alert("An error occured!");
                        }
                    }
                });
            }
        }
    }]);
});