"use strict";
define(["eloue/app", "eloue/constants"], function (EloueApp) {

    /**
     * Factory for managing users.
     */
    EloueApp.factory("Users", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "users/", {},
            {
                "register": { method: "POST", params: {action: "POST"}}
            });
    }]);
});