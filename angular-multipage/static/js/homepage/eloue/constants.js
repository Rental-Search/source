define(["eloue/app"], function (EloueApp) {
    "use strict";

    /**
     * Web service endpoints.
     */
    EloueApp.constant("Endpoints", {
        oauth_url: "http://10.0.0.111:8000/oauth2/",
        api_url: "http://10.0.0.111:8000/api/2.0/"
    });
});