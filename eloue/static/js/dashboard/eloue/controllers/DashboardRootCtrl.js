define([
    "eloue/app",
    "toastr",
    "../../../common/eloue/services/UsersService",
    "../../../common/eloue/services/AuthService",
    "../../../common/eloue/services/UtilsService",
    "../../../common/eloue/services/MapsService"
], function (EloueDashboardApp, toastr) {
    "use strict";
    /**
     * Root controller for the dashboard app.
     */
    EloueDashboardApp.controller("DashboardRootCtrl", [
        "$scope",
        "$window",
        "$document",
        "UsersService",
        "AuthService",
        "UtilsService",
        "MapsService",
        function ($scope, $window, $document, UsersService, AuthService, UtilsService, MapsService) {
            // Read authorization token
            $scope.currentUserToken = AuthService.getUserToken();
            $scope.unreadMessageThreadsCount = 0;
            $scope.newBookingRequestsCount = 0;
            $scope.submitInProgress = false;
            $scope.selectedItem = {};

            $scope.dashboardTabs = [
                {title: "Tableau de bord", icon: "stroke home", sref: "dashboard", badge: 0},
                {title: "Messages", icon: "stroke mail", sref: "messages", badge: 0},
                {title: "Réservations", icon: "stroke calendar-5", sref: "bookings", badge: 0},
                {title: "Annonces", icon: "solid menu-list-4", sref: "items", badge: 0},
                {title: "Compte", icon: "stroke user-4", sref: "account", badge: 0}
            ];

            if ($scope.currentUserToken) {
                // Get current user
                $scope.currentUserPromise = UsersService.getMe();
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    $scope.updateStatistics();
                });
            }

            $scope.updateStatistics = function () {
                UsersService.getStatistics($scope.currentUser.id).then($scope.applyUserStats);
            };

            $scope.applyUserStats = function (stats) {
                $scope.unreadMessageThreadsCount = stats.unread_message_threads_count;
                $scope.newBookingRequestsCount = stats.booking_requests_count;
                $scope.dashboardTabs[1].badge = $scope.unreadMessageThreadsCount;
                $scope.dashboardTabs[2].badge = $scope.newBookingRequestsCount;
            };

            // Set jQuery ajax interceptors
            $.ajaxSetup({
                beforeSend: function (jqXHR) {
                    if ($scope.currentUserToken) {
                        jqXHR.setRequestHeader("Authorization", "Bearer " + $scope.currentUserToken);
                    }
                }
            });

            $scope.clearSelectedItem = function (prefix) {
                delete $scope.selectedItem[prefix];
            };

            $scope.isItemSelected = function (prefix, id) {
                return !!$scope.selectedItem[prefix] && (parseInt($scope.selectedItem[prefix], 10) === parseInt(id, 10));
            };

            $scope.markListItemAsSelected = function (prefix, id) {
                $scope.selectedItem[prefix] = id;
                $("li[id^=" + prefix + "]").each(function () {
                    var item = $(this);
                    if (item.attr("id") === (prefix + id)) {
                        item.addClass("current");
                        item.find(".tab-vertical").addClass("current");
                    } else {
                        item.removeClass("current");
                        item.find(".tab-vertical").removeClass("current");
                    }
                });
            };

            // The method to initiate custom scrollbars
            $scope.initCustomScrollbars = function () {

                // custom scrollbar
                $(".chosen-drop").mCustomScrollbar({
                    scrollInertia: "100",
                    autoHideScrollbar: true,
                    theme: "dark-thin",
                    scrollbarPosition: "outside",
                    advanced: {
                        autoScrollOnFocus: false,
                        updateOnContentResize: true
                    }
                });
                $(".scrollbar-custom").mCustomScrollbar({
                    scrollInertia: "100",
                    autoHideScrollbar: true,
                    theme: "dark-thin",
                    advanced: {
                        updateOnContentResize: true,
                        autoScrollOnFocus: false
                    }
                });
                $(".textarea-wrapper").mCustomScrollbar({
                    scrollInertia: "100",
                    autoHideScrollbar: true,
                    theme: "dark-thin",
                    mouseWheel: {
                        updateOnContentResize: true,
                        disableOver: false
                    }
                });
                $($window).trigger("resize");
            };

            $scope.showNotification = function (object, action, succeed) {
                toastr.options.positionClass = "toast-top-full-width";
                var msg = UtilsService.translate(object) + " " + UtilsService.translate(action) +
                    " " + UtilsService.translate(!succeed ? "fail" : "success");
                if (!succeed) {
                    toastr.error(msg, "");
                } else {
                    toastr.success(msg, "");
                }
            };

            // Nav bar autoresizing
            var dashboardElement = $(".dashboard"),
                dashboard = {
                    article: dashboardElement,
                    nav: dashboardElement.find("nav ul")
                };

            $scope.setProperties = function () {
                var articleHeight = $($window).height() - $("header").height(),
                    navFz = {
                        current: parseFloat(dashboard.nav.css("font-size")),
                        max: 12
                    };

                // set article height
                dashboard.article.height(articleHeight);

                // set nav font-size
                while (dashboard.nav.height() < articleHeight && navFz.max > navFz.current) {
                    dashboard.nav.css("font-size", ++navFz.current + "px");
                }
                while (dashboard.nav.height() >= articleHeight) {
                    dashboard.nav.css("font-size", --navFz.current + "px");
                }
            };

            $scope.setProperties();

            $($window).on("resize", function () {
                $scope.setProperties();
            });

            $window.googleMapsLoaded = function () {
                //Activate geolocation search
                $("#geolocate").formmapper({
                    details: "form"
                });
            };

            MapsService.loadGoogleMaps();

            (function (d, s, id) {
                var js, fjs = d.getElementsByTagName(s)[0];
                if (d.getElementById(id)) {
                    return;
                }
                js = d.createElement(s);
                js.id = id;
                js.src = "//connect.facebook.net/fr_FR/sdk.js#xfbml=1&version=v2.0&appId=197983240245844";
                fjs.parentNode.insertBefore(js, fjs);
            }($document[0], "script", "facebook-jssdk"));
        }
    ]);
});
