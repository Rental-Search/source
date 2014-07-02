define(['angular'], function (angular) {
    'use strict';

    angular.module('eloueApp.controllers.MainCtrl', [])
        .controller('MainCtrl', function ($scope) {
            $scope.awesomeThings = [
                'HTML5 Boilerplate',
                'AngularJS',
                'Karma'
            ];

            $scope.login = function login() {
                $.ajax({
                    url: "http://10.0.0.111:8000/api/2.0/",
                    type: "POST",
                    headers: {
                        Authorization: "Bearer 15aabeed728ff03e93774f59964ab6ca8ceccda7"
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
            };
        });
});
