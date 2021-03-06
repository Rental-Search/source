define(["../../common/eloue/commonApp", "../../common/eloue/values"], function (EloueCommon) {
    "use strict";
    /**
     * Factory for managing users.
     */
    EloueCommon.factory("Users", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "users/:id/?", {},
            {
                "getMe": {method: "GET", params: {id: "me"}},
                "update": {method: "PATCH"},
                "getStats": {method: "GET", url: Endpoints.api_url + "users/:id/stats/?"},
                "send_message": {method: "PUT", url: Endpoints.api_url + "users/:id/send_message/?"}
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
                    headers: {"authorization": ""}
                }
            });
    }]);

    /**
     * Factory for managing message threads.
     */
    EloueCommon.factory("MessageThreads", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "messagethreads/:id/?", {},
            {
                "list": {method: "GET", params: {product: ":productId"}},
                "save": {method: "POST"},
                "isThreadSeen": {method: "GET", url: Endpoints.api_url + "messagethreads/:id/seen/?"}
            });
    }]);

    /**
     * Factory for managing product related messages.
     */
    EloueCommon.factory("ProductRelatedMessages", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "productrelatedmessages/:id/?", {},
            {
                "update": {method: "PUT"},
                "seen": {method: "PUT", url: Endpoints.api_url + "productrelatedmessages/:id/seen/?"},
                "seenBunch": {method: "PUT", url: Endpoints.api_url + "productrelatedmessages/seen/?"}
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
                "getChildren": {method: "GET", url: Endpoints.api_url + "categories/:id/children/?", isArray: true},
                "getAncestors": {method: "GET", url: Endpoints.api_url + "categories/:id/ancestors/?", isArray: true}
            });
    }]);

    /**
     * Factory for managing products.
     */
    EloueCommon.factory("Products", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "products/:id/?", {},
            {
                "update": {method: "PUT"},
                "getStats": {method: "GET", url: Endpoints.api_url + "products/:id/stats/?"},
                "getAbsoluteUrl": {method: "GET", url: Endpoints.api_url + "products/:id/absolute_url/?"},
                "getShippingPoints": {
                    method: "GET",
                    url: Endpoints.api_url + "products/:id/shipping_points/?",
                    isArray: true
                }
            });
    }]);

    /**
     * Factory for checikng availability of product and retrieving product information.
     */
    EloueCommon.factory("CheckAvailability", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "products/:id/is_available/?", {},
            {
                "get": {
                    method: "GET",
                    params: {id: ":id", started_at: ":started_at", ended_at: "ended_at", quantity: ":quantity"}
                }
            });
    }]);

    /**
     * Factory for managing prices.
     */
    EloueCommon.factory("Prices", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "prices/:id/?", {},
            {
                "getProductPricesPerDay": {method: "GET", params: {product: ":productId", unit: "1"}},
                "update": {method: "PUT"}
            });
    }]);

    /**
     * Factory for managing addresses.
     */
    EloueCommon.factory("Addresses", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "addresses/:id/?", {},
            {
                "update": {method: "PUT"}
            });
    }]);

    /**
     * Factory for managing phone numbers.
     */
    EloueCommon.factory("PhoneNumbers", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "phones/:id/?", {},
            {
                "getPremiumRateNumber": {method: "GET", url: Endpoints.api_url + "phones/:id/premium_rate_number/?"},
                "update": {method: "PUT"}
            });
    }]);

    /**
     * Factory for managing professional agencies.
     */
    EloueCommon.factory("ProAgencies", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "pro_agencies/:id/?", {},
            {
                "update": {method: "PUT"}
            });
    }]);

    /**
     * Factory for managing bookings.
     */
    EloueCommon.factory("Bookings", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "bookings/:uuid/?", {},
            {
                "pay": {method: "PUT", url: Endpoints.api_url + "bookings/:uuid/pay/?"},
                "accept": {method: "PUT", url: Endpoints.api_url + "bookings/:uuid/accept/?"},
                "reject": {method: "PUT", url: Endpoints.api_url + "bookings/:uuid/reject/?"},
                "cancel": {method: "PUT", url: Endpoints.api_url + "bookings/:uuid/cancel/?"},
                "incident": {method: "PUT", url: Endpoints.api_url + "bookings/:uuid/incident/?"}
            });
    }]);

    /**
     * Factory for managing pictures.
     */
    EloueCommon.factory("Pictures", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "pictures/:id/?");
    }]);

    /**
     * Factory for managing comments.
     */
    EloueCommon.factory("Comments", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "comments/:id/?");
    }]);

    /**
     * Factory for managing sinisters.
     */
    EloueCommon.factory("Sinisters", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "sinisters/:id/?");
    }]);

    /**
     * Factory for managing shippings.
     */
    EloueCommon.factory("Shippings", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "shippings/:id/?");
    }]);

    /**
     * Factory for managing shipping points.
     */
    EloueCommon.factory("ShippingPoints", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "shippingpoints/:id/?", {},
            {
                "get": {method: "GET", isArray: true}
            });
    }]);

    /**
     * Factory for managing product shipping points.
     */
    EloueCommon.factory("ProductShippingPoints", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "productshippingpoints/:id/?");
    }]);

    /**
     * Factory for managing patron shipping points.
     */
    EloueCommon.factory("PatronShippingPoints", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "patronshippingpoints/:id/?");
    }]);

    /**
     * Factory for managing product unavailability periods.
     */
    EloueCommon.factory("UnavailabilityPeriods", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "unavailabilityperiods/:id/?", {},
            {
                "update": {method: "PUT"}
            });
    }]);

    /**
     * Factory for credit cards.
     */
    EloueCommon.factory("CreditCards", ["$resource", "Endpoints", function ($resource, Endpoints) {
        return $resource(Endpoints.api_url + "credit_cards/:id/?", {},
            {
                "update": {method: "PUT"}
            });
    }]);
});
