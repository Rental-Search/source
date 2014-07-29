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

    /**
     * Factory for managing message threads.
     */
    EloueApp.factory("MessageThreads", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "messagethreads\\/", {},
            {
                "list": { method: "GET", params: {product: ":productId"}},
                "save": {method: "POST"}
            });
    }]);

    /**
     * Factory for managing product related messages.
     */
    EloueApp.factory("ProductRelatedMessages", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "productrelatedmessages\\/", {},
            {
                "get": { method: "GET", url: Endpoints.api_url + "productrelatedmessages/:id\\/", params: {id: ":id"}},
                "save": {method: "POST"}
            });
    }]);

    /**
     * Factory for managing contacts.
     */
    EloueApp.factory("Contacts", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource("data/contacts.json", {},
            {
                "get": { method: "GET"}
            });
    }]);

    /**
     * Factory for managing products.
     */
    EloueApp.factory("Products", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "products/:id\\/", {},
            {
                "get": { method: "GET", params: {id: ":id"}}
            });
    }]);

    /**
     * Factory for checking product availability and price information.
     */
    EloueApp.factory("CheckAvailability", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "products/:id/is_available\\/", {},
            {
                "get": { method: "GET", params: {id: ":id", started_at: ":started_at", ended_at: "ended_at", quantity: ":quantity"}}
            });
    }]);

    /**
     * Factory for managing prices.
     */
    EloueApp.factory("Prices", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "prices\\/", {},
            {
                "get": { method: "GET", params: {product: ":productId", unit: "1"}}
            });
    }]);

    /**
     * Factory for managing addresses.
     */
    EloueApp.factory("Addresses", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "addresses/:id\\/", {},
            {
                "get": { method: "GET", params: {id: ":id"}}
            });
    }]);

    /**
     * Factory for managing phone numbers.
     */
    EloueApp.factory("PhoneNumbers", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "phonenumbers/:id\\/", {},
            {
                "get": { method: "GET", params: {id: ":id"}}
            });
    }]);
});