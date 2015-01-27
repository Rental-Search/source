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

        return utilsService;
    }]);
});
