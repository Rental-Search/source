define(["../../../common/eloue/commonApp", "../../../common/eloue/services/AuthService"], function (EloueCommon) {
    "use strict";
    /**
     * Utils service.
     */
    EloueCommon.factory("UtilsService", ["$filter", "AuthService", function ($filter, AuthService) {
        var utilsService = {};

        utilsService.formatDate = function (date, format) {
            return $filter("date")(date, format);
        };

        /**
         * Translates message using provided key.
         * @param msgKey message key for eloue/static/js/common/eloue/i18n.js
         * @returns Translation
         */
        utilsService.translate = function (msgKey) {
            return $filter("translate")(msgKey);
        };

        utilsService.formatMessageDate = function (dateString, shortFormat, fullFormat) {
            var sentDate = new Date(dateString), nowDate = new Date(), dateFormat;
            // If date is today
            if (sentDate.setHours(0, 0, 0, 0) === nowDate.setHours(0, 0, 0, 0)) {
                dateFormat = shortFormat;
            } else {
                dateFormat = fullFormat;
            }
            return this.formatDate(sentDate, dateFormat);
        };

        utilsService.getIdFromUrl = function (url) {
            var trimmedUrl = url.slice(0, url.length - 1);
            return trimmedUrl.substring(trimmedUrl.lastIndexOf("/") + 1, url.length);
        };

        utilsService.calculatePeriodBetweenDates = function (startDateString, endDateString) {
            var hourTime = 60 * 60 * 1000,
                dayTime = 24 * hourTime,
                startTime = Date.parse(startDateString).getTime(),
                endTime = Date.parse(endDateString).getTime(),
                diffTime = endTime - startTime,
                periodDays = Math.floor(diffTime / dayTime),
                periodHours = Math.floor((diffTime - dayTime * periodDays) / hourTime);
            return {
                period_days: periodDays,
                period_hours: periodHours
            };
        };

        utilsService.isToday = function (dateStr) {
            var date = Date.parse(dateStr), today = new Date();
            return !!date && date.getDate() === today.getDate() && date.getMonth() === today.getMonth() && date.getFullYear() === today.getFullYear();
        };

        utilsService.downloadPdfFile = function (url, filename) {
            var xhr = new XMLHttpRequest(),
                userToken = AuthService.getUserToken(),
                csrftoken = AuthService.getCSRFToken();
            xhr.open("GET", url, true);
            if (userToken && userToken.length > 0) {
                xhr.setRequestHeader("Authorization", "Bearer " + userToken);
            }
            if (csrftoken && csrftoken.length > 0) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
            xhr.responseType = "blob";

            xhr.onload = function (e) {
                if (this.status === 200) {
                    var file = new Blob([this.response], {type: "application/pdf"});
                    saveAs(file, filename);
                }
            };

            xhr.send();
        };

        /**
         * Set valid sender for messages.
         * @param messages messages to modify.
         * @param replacer in case of sender is not current user, sender filed will be replaced with this object.
         * @param currentUser current user.
         */
        utilsService.updateMessagesSender = function(messages, replacer, currentUser) {
            // Replace sender as url with real object for all messages.
            for (var i = 0; i < messages.length; i++) {
                if (angular.isObject(messages[i].sender)) {
                    continue;
                }
                var senderId = utilsService.getIdFromUrl(messages[i].sender);

                if (senderId == replacer.id) {
                    messages[i].sender = replacer;
                } else {
                    messages[i].sender = currentUser;
                }
            }
        };

        /**
         * Get unread messages ids.
         * @param messages messages to check.
         * @param currentUser current user to prevent selecting outcoming messages.
         * @returns {Array} array of unread messages ids.
         */
        utilsService.getUnreadMessagesIds = function(messages, currentUser) {
            var unreadMessagesIds = [];
            for (var i = 0; i < messages.length; i++) {
                if (messages[i].read_at == null && (messages[i].sender.id != currentUser.id || messages[i].sender.id == utilsService.getIdFromUrl(messages[i].recipient))) {
                    unreadMessagesIds.push(messages[i].id);
                }
            }
            return unreadMessagesIds;
        };

        // The method to initiate custom scrollbars
        utilsService.initCustomScrollbars = function(scrollbarSelector) {

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
                $(scrollbarSelector ? scrollbarSelector : ".scrollbar-custom").mCustomScrollbar({
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
            };

        utilsService.getQueryParams = function () {
            var query_string = [];
            var query = decodeURIComponent(window.location.search.substring(1));
            var vars = query.split("&");
            for (var i = 0; i < vars.length; i++) {
                var pair = vars[i].split("=");
                // If first entry with this name
                if (typeof query_string[pair[0]] === "undefined") {
                    query_string[pair[0]] = pair[1];
                    // If second entry with this name
                } else if (typeof query_string[pair[0]] === "string") {
                    query_string[pair[0]] = [query_string[pair[0]], pair[1]];
                    // If third or later entry with this name
                } else {
                    query_string[pair[0]].push(pair[1]);
                }
            }
            return query_string;
        };

        return utilsService;
    }]);
});
