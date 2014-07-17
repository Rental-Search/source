"use strict";
define(["eloue/app", "eloue/constants"], function (EloueApp) {

    /**
     * Factory for managing users.
     */
    EloueApp.factory("Users", ["$resource", "Endpoints", function ($resource, Endpoints) {
        var userToken = "4f39963a7664e77d12100f833a49784e94b3650c";
        return $resource(Endpoints.api_url + "users/:id", {},
            {
                "get": { method: "GET",headers: {Authorization: "Bearer " + userToken}},
                "register": { method: "POST", params: {action: "POST"}}
            });
    }]);

    EloueApp.factory("Messages", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource("data/messagethreads.json", {},
            {
                "list": { method: "GET"}
            });
    }]);

    EloueApp.factory("Contacts", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource("data/contacts.json", {},
            {
                "get": { method: "GET"}
            });
    }]);

});