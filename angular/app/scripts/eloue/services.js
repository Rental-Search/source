"use strict";
define(["eloue/app", "eloue/constants"], function (EloueApp) {

    /**
     * Factory for managing users.
     */
    EloueApp.factory("Users", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "users/:id\\/", {},
            {
                "get": { method: "GET", params: {id: ":id"}},
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

    EloueApp.factory("Products", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "products/:id\\/", {},
            {
                "get": { method: "GET", params: {id: ":id"}}
            });
    }]);

    EloueApp.factory("CheckAvailability", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "products/:id/is_available\\/", {},
            {
                "get": { method: "GET", params: {id: ":id", started_at: ":started_at", ended_at: "ended_at", quantity: ":quantity"}}
            });
    }]);

    EloueApp.factory("Prices", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "prices\\/", {},
            {
                "get": { method: "GET", params: {product: ":productId", unit: "1"}}
            });
    }]);

    EloueApp.factory("Addresses", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "addresses/:id\\/", {},
            {
                "get": { method: "GET", params: {id: ":id"}}
            });
    }]);

    EloueApp.factory("PhoneNumbers", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "phonenumbers/:id\\/", {},
            {
                "get": { method: "GET", params: {id: ":id"}}
            });
    }]);
});