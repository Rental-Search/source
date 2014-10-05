"use strict";

define(["angular", "eloue/app", "../../../common/eloue/services", "../../../common/eloue/controllers", "../../../common/eloue/directives"], function (angular) {

    /**
     * Root controller for the dashboard app.
     */
    angular.module("EloueDashboardApp").controller("DashboardRootCtrl", [
        "$scope",
        "UsersService",
        "AuthService",
        function ($scope, UsersService, AuthService) {
            // Read authorization token
            $scope.currentUserToken = AuthService.getCookie("user_token");
            $scope.unreadMessageThreadsCount = 0;
            $scope.newBookingRequestsCount = 0;
            $scope.dashboardTabs = [
                {title: 'Dashboard', icon: 'stroke home', sref: 'dashboard', badge: 0},
                {title: 'Messages', icon: 'stroke mail', sref: 'messages', badge: 0},
                {title: 'Booking', icon: 'stroke calendar-5', sref: 'bookings', badge: 0},
                {title: 'Items', icon: 'solid menu-list-4', sref: 'items', badge: 0},
                {title: 'Account', icon: 'stroke user-4', sref: 'account', badge: 0}
            ];

            if (!!$scope.currentUserToken) {
                // Get current user
                $scope.currentUserPromise = UsersService.getMe().$promise;
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    UsersService.getStatistics($scope.currentUser.id).$promise.then(function (stats) {
                        $scope.unreadMessageThreadsCount = stats.unread_message_threads_count;
                        $scope.newBookingRequestsCount = stats.booking_requests_count;
                        $scope.dashboardTabs[1].badge = $scope.unreadMessageThreadsCount;
                        $scope.dashboardTabs[2].badge = $scope.newBookingRequestsCount;
                    });
                });
            }

            // Set jQuery ajax interceptors
            $.ajaxSetup({
                beforeSend: function (jqXHR) {
                    if (!!$scope.currentUserToken) {
                        jqXHR.setRequestHeader("Authorization", "Bearer " + $scope.currentUserToken);
                    }
                }
            });

            $scope.markListItemAsSelected = function(prefix, id) {
                $('li[id^=' + prefix + ']').each(function () {
                    var item = $(this);
                    if (item.attr("id") == (prefix + id)) {
                        item.addClass("current");
                    } else {
                        item.removeClass("current");
                    }
                });
            };

            // The method to initiate custom scrollbars
            $scope.initCustomScrollbars = function () {

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

            window.googleMapsLoaded = function () {
                //Activate geolocation search
                $('#geolocate').formmapper({
                    details: "form"
                });
            };

            function loadGoogleMaps() {
                var script = document.createElement("script");
                script.type = "text/javascript";
                script.src = "http://maps.googleapis.com/maps/api/js?sensor=false&libraries=places&language=fr&callback=googleMapsLoaded";
                document.body.appendChild(script);
            }
            loadGoogleMaps();
        }
    ]);
});