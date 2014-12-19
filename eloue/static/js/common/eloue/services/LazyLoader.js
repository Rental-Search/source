"use strict";
define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values"], function (EloueCommon) {
    /**
     * List lazy loading service (used fot lazy load lists of messages, bookings and items in dashboard).
     */
    EloueCommon.factory("LazyLoader", ["$timeout", "$rootScope", "$q", function ($timeout, $rootScope, $q) {
        var config,
            data,
            fetch,
            args;
        return {

            configure: function (options) {
                config = options;
                data = config.data;
                fetch = config.fetchData;
                args = config.args;
            },

            getData: function () {
                var deferred = $q.defer();
                $rootScope.$broadcast("showLoading");

                fetch.apply(null, args).then(function (res) {
                    deferred.resolve(res);
                    $rootScope.$broadcast("hideLoading");
                });

                return deferred.promise;
            },

            load: function () {
                var deferred = $q.defer();
                var _this = this;

                $rootScope.$broadcast("showLoading");

                _this.getData().then(function (col) {
                    deferred.resolve(col);
                });

                return deferred.promise;
            }
        };
    }]);
});
