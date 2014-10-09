"use strict";
define(["../../common/eloue/commonApp", "../../common/eloue/values"], function (EloueCommon) {

    /**
     * Factory for managing users.
     */
    EloueCommon.factory("Users", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "users/:id/?", {},
            {
                "getMe": { method: "GET", params: {id: "me"} },
                "update": { method: "PATCH" },
                "getStats": { method: "GET", url: Endpoints.api_url + "users/:id/stats/?" }
            });
    }]);

    /**
     * Factory for user registration.
     */
    EloueCommon.factory("Registration", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "users/?", {},
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
        return $resource(Endpoints.api_url + "messagethreads/:id/?", {},
            {
                "list": { method: "GET", params: {product: ":productId"}},
                "save": {method: "POST"}
            });
    }]);

    /**
     * Factory for managing product related messages.
     */
    EloueCommon.factory("ProductRelatedMessages", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "productrelatedmessages/?", {},
            {
                "get": { method: "GET", url: Endpoints.api_url + "productrelatedmessages/:id/?", params: {id: ":id"}},
                "save": {method: "POST"}
            });
    }]);

    /**
     * Factory for managing contacts.
     */
    EloueCommon.factory("Contacts", ["$resource", function ($resource) {
        return $resource("data/contacts.json");
    }]);

    /**
     * Factory for managing categories.
     */
    EloueCommon.factory("Categories", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "categories/:id/?", {},
            {
                "getChildren": { method: "GET", url: Endpoints.api_url + "categories/:id/children/?", isArray: true}
            });
    }]);

    /**
     * Factory for managing products.
     */
    EloueCommon.factory("Products", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "products/:id/?", {},
            {
                "update": { method: "PUT" },
                "getStats": { method: "GET", url: Endpoints.api_url + "products/:id/stats/?" }
            });
    }]);

    /**
     * Factory for checikng availability of product and retrieving product information.
     */
    EloueCommon.factory("CheckAvailability", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "products/:id/is_available/?", {},
            {
                "get": { method: "GET", params: {id: ":id", started_at: ":started_at", ended_at: "ended_at", quantity: ":quantity"}}
            });
    }]);

    /**
     * Factory for managing prices.
     */
    EloueCommon.factory("Prices", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "prices/:id/?", {},
            {
                "getProductPricesPerDay": { method: "GET", params: {product: ":productId", unit: "1"}},
                "update": { method: "PUT" }
            });
    }]);

    /**
     * Factory for managing addresses.
     */
    EloueCommon.factory("Addresses", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "addresses/:id/?", {},
            {
                "update": { method: "PUT" }
            });
    }]);

    /**
     * Factory for managing phone numbers.
     */
    EloueCommon.factory("PhoneNumbers", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "phones/:id/?", {},
            {
                "getPremiumRateNumber": { method: "GET", url: Endpoints.api_url + "phones/:id/premium_rate_number/?" },
                "update": { method: "PUT" }
            });
    }]);

    /**
     * Factory for managing professional agencies.
     */
    EloueCommon.factory("ProAgencies", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "pro_agencies/:id/?", {},
            {
                "update": { method: "PUT" }
            });
    }]);

    /**
     * Factory for managing bookings.
     */
    EloueCommon.factory("Bookings", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "bookings/:uuid/?", {},
            {
                "pay": { method: "PUT", url: Endpoints.api_url + "bookings/:uuid/pay/?"}
            });
    }]);

    /**
     * Factory for managing pictures.
     */
    EloueCommon.factory("Pictures", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "pictures/?");
    }]);

    /**
     * Factory for managing comments.
     */
    EloueCommon.factory("Comments", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "comments/:id/?");
    }]);

    /**
     * Factory for credit cards.
     */
    EloueCommon.factory("CreditCards", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "credit_cards/:id/?", {},
            {
                "update": { method: "PUT" }
            });
    }]);
});