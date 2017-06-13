define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values"], function (EloueCommon) {
    "use strict";
    /**
     * List lazy loading service (used fot lazy load lists of messages, bookings and items in dashboard).
     */
    EloueCommon.factory("LazyLoader", ["$timeout", "$rootScope", "$q", function ($timeout, $rootScope, $q) {
        var config,
            data,
            fetch,
            args,
            showLoadingEventName,
            hideLoadingEventName;
        return {

            configure: function (options) {
                config = options;
                data = config.data;
                fetch = config.fetchData;
                args = config.args;
                showLoadingEventName = config.showLoadingEventName;
                hideLoadingEventName = config.hideLoadingEventName;
            },

            getData: function () {
                var deferred = $q.defer();
                $rootScope.$broadcast(showLoadingEventName);

                fetch.apply(null, args).then(function (res) {
                    deferred.resolve(res);
                    $rootScope.$broadcast(hideLoadingEventName);
                }, function(error) {
                    deferred.reject(error);
                });

                return deferred.promise;
            },

            load: function () {
                var deferred = $q.defer();

                $rootScope.$broadcast(showLoadingEventName);

                this.getData().then(function (col) {
                    deferred.resolve(col);
                }, function(error) {
                    deferred.reject(error);
                });

                return deferred.promise;
            }
        };
    }]);
});
