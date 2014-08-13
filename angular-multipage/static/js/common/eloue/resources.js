"use strict";
define(["../../common/eloue/commonApp", "../../common/eloue/values"], function (EloueCommon) {

    /**
     * Factory for managing users.
     */
    EloueCommon.factory("Users", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "users/:id\\/", {},
            {
                "getMe": { method: "GET", params: {id: "me"} }
            });
    }]);

    /**
     * Factory for user registration.
     */
    EloueCommon.factory("Registration", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "users\\/", {},
            {
                "register": {
                    method: "POST",
                    headers: { 'authorization': '' }
                }
            });
    }]);

    /**
     * Factory for managing message threads.
     */
    EloueCommon.factory("MessageThreads", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "messagethreads/:id/", {},
            {
                "list": { method: "GET", params: {product: ":productId"}},
                "save": {method: "POST"}
            });
    }]);

    /**
     * Factory for managing product related messages.
     */
    EloueCommon.factory("ProductRelatedMessages", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "productrelatedmessages\\/", {},
            {
                "get": { method: "GET", url: Endpoints.api_url + "productrelatedmessages/:id\\/", params: {id: ":id"}},
                "save": {method: "POST"}
            });
    }]);

    /**
     * Factory for managing contacts.
     */
    EloueCommon.factory("Contacts", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource("data/contacts.json", {},
            {
                "get": { method: "GET"}
            });
    }]);

    /**
     * Factory for managing products.
     */
    EloueCommon.factory("Products", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "products/:id\\/", {},
            {
                "get": { method: "GET", params: {id: ":id"}}
            });
    }]);

    /**
     * Factory for checikng availability of product and retrieving product information.
     */
    EloueCommon.factory("CheckAvailability", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "products/:id/is_available\\/", {},
            {
                "get": { method: "GET", params: {id: ":id", started_at: ":started_at", ended_at: "ended_at", quantity: ":quantity"}}
            });
    }]);

    /**
     * Factory for managing prices.
     */
    EloueCommon.factory("Prices", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "prices\\/", {},
            {
                "get": { method: "GET", params: {product: ":productId", unit: "1"}}
            });
    }]);

    /**
     * Factory for managing addresses.
     */
    EloueCommon.factory("Addresses", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "addresses/:id\\/", {},
            {
                "get": { method: "GET", params: {id: ":id"}}
            });
    }]);

    /**
     * Factory for managing phone numbers.
     */
    EloueCommon.factory("PhoneNumbers", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "phonenumbers/:id\\/", {},
            {
                "get": { method: "GET", params: {id: ":id"}}
            });
    }]);

    /**
     * Factory for managing bookings.
     */
    EloueCommon.factory("Bookings", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "bookings/:uuid/?");
    }]);

    /**
     * Factory for managing pictures.
     */
    EloueCommon.factory("Pictures", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "pictures\\/");
    }]);
});