define(["../../common/eloue/commonApp"], function (EloueCommon) {

    "use strict";

    /**
     * Web service endpoints.
     */
    EloueCommon.constant("Endpoints", {
        oauth_url: "http://10.0.0.111:8000/oauth2/",
        api_url: "http://10.0.0.111:8000/api/2.0/"
    });

    /**
     * URL to redirect user after logging in.
     */
    EloueCommon.value("RedirectAfterLogin", { url: "/"});
});