"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Root controller for the dashboard app.
     */
    angular.module("EloueDashboardApp").controller("DashboardRootCtrl", [
        "$scope",
        "$cookies",
        function ($scope, $cookies) {
            // Read authorization token
            $scope.currentUserToken = $cookies.user_token;

            // Set jQuery ajax interceptors
            $.ajaxSetup({
                beforeSend: function (jqXHR) {
                    if (!!$scope.currentUserToken) {
                        jqXHR.setRequestHeader("authorization", "Bearer " + $scope.currentUserToken);
                    }
                }
            });

            // Nav bar autoresizing
            var dashboardElement = $('.dashboard');
            var dashboard = {
                article: dashboardElement,
                nav: dashboardElement.find('nav ul')
            };

            function setProperties() {
                var article_height = $(window).height() - $('header').height(),
                    nav_fz = {
                        current: parseFloat(dashboard.nav.css('font-size')),
                        max: 12
                    };

                // set article height
                dashboard.article.height(article_height);

                // set nav font-size
                while(dashboard.nav.height() < article_height && nav_fz.max > nav_fz.current) {
                    dashboard.nav.css('font-size', ++nav_fz.current + 'px');
                }
                while(dashboard.nav.height() >= article_height) {
                    dashboard.nav.css('font-size', --nav_fz.current + 'px');
                }
            }

            setProperties();

            $(window).on('resize', function() {
                setProperties();
            });
        }
    ]);
});