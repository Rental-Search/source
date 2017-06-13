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
        "$q",
        "$scope",
        "$window",
        "$document",
        "UsersService",
        "AuthService",
        "UtilsService",
        "MapsService",
        function ($q, $scope, $window, $document, UsersService, AuthService, UtilsService, MapsService) {
            // Read authorization token
            $scope.currentUserToken = AuthService.getUserToken();
            $scope.unreadMessageThreadsCount = 0;
            $scope.newBookingRequestsCount = 0;
            $scope.submitInProgress = false;
            $scope.selectedItem = {};
            
            $scope.loadedPromise = $q.when();
            
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
                $scope.loadedPromise = $scope.currentUserPromise
                .then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    $scope.updateStatistics();
                }).then(function(){
                    NProgress.move(0.3);
                });
            }

            $scope.updateStatistics = function () {
                UsersService.getStatistics($scope.currentUser.id)
                .then($scope.applyUserStats);
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

            /**
             * Show toastr with provided message.
             * @param msg Message to be shown.
             * @param succeed Action result. true means success, false means error.
             */
            $scope.showNotificationMessage = function(msg, succeed) {
                toastr.options.positionClass = "toast-top-full-width";
                if (!succeed) {
                    toastr.error(msg, "");
                } else {
                    toastr.success(msg, "");
                }
            };

            /**
             * Shows toastr with built message. Message consists of object that produced the action, the action
             * that was generated by the object, and action status (succeed or failed).
             */
            $scope.showNotification = function (object, action, succeed) {
                
                // Get object
                var obj_parts = UtilsService.translate(object.toUpperCase()).split('|');
                var params = {
                    OBJECT:obj_parts[0],
                    GENDER:obj_parts[1],
                    NUM:parseInt(obj_parts[2]),
                    SUCCESS:succeed
                };
                
                // Translate action
                var action = UtilsService.translate(action.toUpperCase(), params, 'messageformat');
                params.ACTION = action;
                
                // Generate message
                var msg = UtilsService.translate('DASHBOARD_SUBMIT', params, 'messageformat');
                
                // Ensure first capital letter
                msg = msg.charAt(0).toUpperCase() + msg.slice(1);
                
                $scope.showNotificationMessage(msg, succeed);
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
                $scope.loadedPromise = $scope.loadedPromise
                .then(function(){
                    NProgress.move(0.3); 
                });
            };
            
            $scope.loadedPromise.finally(function(){
                completePageLoad();
            });
            
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
