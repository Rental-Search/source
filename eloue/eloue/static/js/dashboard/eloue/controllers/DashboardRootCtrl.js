"use strict";

define(["angular", "eloue/app", "../../../common/eloue/services", "../../../common/eloue/controllers", "../../../common/eloue/directives"], function (angular) {

    /**
     * Root controller for the dashboard app.
     */
    angular.module("EloueDashboardApp").controller("DashboardRootCtrl", [
        "$scope",
        "$cookies",
        "UsersService",
        function ($scope, $cookies, UsersService) {
            // Read authorization token
            $scope.currentUserToken = $cookies.user_token;

            // Get current user
            $scope.currentUserPromise = UsersService.getMe().$promise;

            // TODO: Retrieve counts for icons' badges
            $scope.unreadMessageThreadsCount = 2;
            $scope.newBookingRequestsCount = 1;
            $scope.accountRating = 4;

            // Set jQuery ajax interceptors
            $.ajaxSetup({
                beforeSend: function (jqXHR) {
                    if (!!$scope.currentUserToken) {
                        jqXHR.setRequestHeader("authorization", "Bearer " + $scope.currentUserToken);
                    }
                }
            });

            // The method to initiate custom scrollbars
            $scope.initCustomScrollbars = function () {
                // custom select
                //TODO: fix problem with select options model update
//                $('select').chosen();

                // custom scrollbar
                $('.chosen-drop').mCustomScrollbar({
                    scrollInertia: '100',
                    autoHideScrollbar: true,
                    theme: 'dark-thin',
                    scrollbarPosition: 'outside',
                    advanced:{
                        autoScrollOnFocus: false,
                        updateOnContentResize: true
                    }
                });
                $('.scrollbar-custom').mCustomScrollbar({
                    scrollInertia: '100',
                    autoHideScrollbar: true,
                    theme: 'dark-thin',
                    advanced:{
                        updateOnContentResize: true,
                        autoScrollOnFocus: false
                    }
                });
                $('.textarea-wrapper').mCustomScrollbar({
                    scrollInertia: '100',
                    autoHideScrollbar: true,
                    theme: 'dark-thin',
                    mouseWheel:{
                        disableOver: false
                    }
                });
            };

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