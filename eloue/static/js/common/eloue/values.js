define(["../../common/eloue/commonApp"], function (EloueCommon) {

    "use strict";

    /**
     * Web service endpoints.
     */
    EloueCommon.constant("Endpoints", {
        oauth_url: "/oauth2/",
        api_url: "/api/2.0/"
    });

    EloueCommon.constant("AuthConstants", {
        clientId: "51bcafe59e484b028657",
        clientSecret: "132a8a395c140e29f15c4341758c59faa33e012b",
        grantType: "password"
    });

    EloueCommon.constant("Path", {
        templatePrefix: "/" // FIXME: should use /templates/ for local files, and / if HTTP scheme is HTTP/HTTPS
    });

    EloueCommon.constant("ServiceErrors", {
        "invalid_grant": "Bad credentials provided",
        "invalid_request": "Bad request",
        "invalid_scope": "Invalid scope",
        "invalid_client": "Wrong client app",
        "user_inactive": "Votre compte est inactif."
    });

    EloueCommon.constant("ActivityType", {
        "ALL": {id: "0", name: "All"},
        "MESSAGE": {id: "1", name: "Messages"},
        "BOOKING": {id: "2", name: "Bookings"},
        "ITEM": {id: "3", name: "Items"},
        "ACCOUNT": {id: "4", name: "Accounts"}
    });

    EloueCommon.constant("CivilityChoices",{ 
        'fr':{
            "MME": {id: "0", name: "Mme"},
            "MLLE": {id: "1", name: "Mlle"},
            "M": {id: "2", name: "Mr"}
        },
        'en-US':{
            "MME": {id: "0", name: "Ms"},
            "M": {id: "2", name: "Mr"}
        }
    });

    EloueCommon.constant("Currency", {
        "EUR": {name: "EUR", symbol: "€"},
        "USD": {name: "USD", symbol: "$"},
        "GBP": {name: "GPB", symbol: "£"},
        "JPY": {name: "YEN", symbol: "¥"},
        "XPF": {name: "XPF", symbol: "F"},
        "DKK": {name: "DKK", symbol: "kr."},
    });

    EloueCommon.constant("Unit", {
        "HOUR": {id: 0, name: "heure", description: "1 heure"},
        "DAY": {id: 1, name: "", description: ""},
        "WEEK_END": {id: 2, name: "jour", description: "1 jour"},
        "WEEK": {id: 3, name: "semaine", description: "1 semaine"},
        "TWO_WEEKS": {id: 4, name: "deux semaines", description: "2 semaines"},
        "MONTH": {id: 5, name: "mois", description: "1 mois"},
        "THREE_DAYS": {id: 6, name: "3jours", description: "3 jours"},
        "FIFTEEN_DAYS": {id: 7, name: "15jours", description: "15 jours"}
    });

    EloueCommon.constant("SeatNumber", {
        "2": {id: 2, name: "2"},
        "3": {id: 3, name: "3"},
        "4": {id: 4, name: "4"},
        "5": {id: 5, name: "5"},
        "6": {id: 6, name: "6"},
        "7": {id: 7, name: "7"},
        "8": {id: 8, name: "8"},
        "9": {id: 9, name: "9"},
        "10": {id: 10, name: "10"}
    });

    EloueCommon.constant("DoorNumber", {
        "2": {id: 2, name: "2"},
        "3": {id: 3, name: "3"},
        "4": {id: 4, name: "4"},
        "5": {id: 5, name: "5"},
        "6": {id: 6, name: "6"}
    });

    EloueCommon.constant("Consumption", {
        "2": {id: 2, name: "2"},
        "3": {id: 3, name: "3"},
        "4": {id: 4, name: "4"},
        "5": {id: 5, name: "5"},
        "6": {id: 6, name: "6"},
        "7": {id: 7, name: "7"},
        "8": {id: 8, name: "8"},
        "9": {id: 9, name: "9"},
        "10": {id: 10, name: "10"},
        "11": {id: 11, name: "11"},
        "12": {id: 12, name: "12"},
        "13": {id: 13, name: "13"},
        "14": {id: 14, name: "14"},
        "15": {id: 15, name: "15"},
        "16": {id: 16, name: "16"},
        "17": {id: 17, name: "17"},
        "18": {id: 18, name: "18"},
        "19": {id: 19, name: "19"}
    });

    EloueCommon.constant("Fuel", {
        "1": {id: 1, name: "Essence"},
        "2": {id: 2, name: "Diesel"},
        "3": {id: 3, name: "GPL"},
        "4": {id: 4, name: "Electrique"},
        "5": {id: 5, name: "Hybride"}
    });

    EloueCommon.constant("Transmission", {
        "1": {id: 1, name: "Manuel"},
        "2": {id: 2, name: "Automatique"}
    });

    EloueCommon.constant("Mileage", {
        "1": {id: 1, name: "- de 10000 km'"},
        "2": {id: 2, name: "Entre 10001 et 50000 km"},
        "3": {id: 3, name: "Plus de 50000 km"}
    });

    EloueCommon.constant("Capacity", {
        "1": {id: 1, name: "1"},
        "2": {id: 2, name: "2"},
        "3": {id: 3, name: "3"},
        "4": {id: 4, name: "4"},
        "5": {id: 5, name: "5"},
        "6": {id: 6, name: "6"},
        "7": {id: 7, name: "7"},
        "8": {id: 8, name: "8"},
        "9": {id: 9, name: "9"},
        "10": {id: 10, name: "10"},
        "11": {id: 11, name: "11"},
        "12": {id: 12, name: "12"},
        "13": {id: 13, name: "13"},
        "14": {id: 14, name: "14"},
        "15": {id: 15, name: "15"},
        "16": {id: 16, name: "16"},
        "17": {id: 17, name: "17"},
        "18": {id: 18, name: "18"},
        "19": {id: 19, name: "19+"}
    });

    EloueCommon.constant("PrivateLife", {
        "1": {id: 1, name: "Appartement/Maison"},
        "2": {id: 2, name: "Chambre partagé"},
        "3": {id: 3, name: "Chambre privée"}
    });

    /**
     * URL to redirect user after logging in.
     */
    EloueCommon.value("RedirectAfterLogin", {url: "/"});

    /**
     * Svg cannot parse <image xlink:href> as URL. Base64 data is acceptable.
     * All marker images are converted to Base64.
     */
    EloueCommon.value("GoogleMapsMarkers", {
        smallMarkerPath: "M 12.80 0.00 L 15.35 0.00 C 18.27 0.95 21.17 2.57 22.66 5.37 C 25.06 9.50 24.18 15.32 20.35 18.30 C 17.69 20.50 15.95 23.51 13.98 26.29 C 11.98 22.61 8.98 19.79 5.61 17.41 C -0.22 11.38 4.44 0.25 12.80 0.00 Z",

        largeMarkerPath: "M 9.92 0.00 L 18.37 0.00 C 22.82 1.16 26.59 4.84 27.00 9.55 L 27.00 11.73 C 26.42 16.38 22.69 19.83 18.33 21.04 C 16.95 23.04 15.66 25.11 14.14 27.00 L 13.77 27.00 C 12.39 25.08 11.08 23.10 9.74 21.14 C 4.78 20.43 0.38 16.54 0.00 11.38 L 0.00 9.34 C 0.61 4.38 4.90 0.27 9.92 0.00 Z",

        template: [
            '<?xml version="1.0"?>',
            '<svg height="27" width="27" version="1.1" viewBox="0 0 27 27" xmlns="http://www.w3.org/2000/svg">',
            '<path fill="{{markerColor}}" stroke="none" stroke-width="0" d="{{markerPath}}" />',
            '<text text-anchor="middle" font-family="Open Sans" font-weight="600" y="14" x="13" font-size="10" fill="#FFFFFF">{{markerLabel}}</text>',
            '</svg>'
        ].join('\n')
    });

    EloueCommon.value("AvailableHours", [
        {"label": "00h", "value": "00:00:00"},
        {"label": "01h", "value": "01:00:00"},
        {"label": "02h", "value": "02:00:00"},
        {"label": "03h", "value": "03:00:00"},
        {"label": "04h", "value": "04:00:00"},
        {"label": "05h", "value": "05:00:00"},
        {"label": "06h", "value": "06:00:00"},
        {"label": "07h", "value": "07:00:00"},
        {"label": "08h", "value": "08:00:00"},
        {"label": "09h", "value": "09:00:00"},
        {"label": "10h", "value": "10:00:00"},
        {"label": "11h", "value": "11:00:00"},
        {"label": "12h", "value": "12:00:00"},
        {"label": "13h", "value": "13:00:00"},
        {"label": "14h", "value": "14:00:00"},
        {"label": "15h", "value": "15:00:00"},
        {"label": "16h", "value": "16:00:00"},
        {"label": "17h", "value": "17:00:00"},
        {"label": "18h", "value": "18:00:00"},
        {"label": "19h", "value": "19:00:00"},
        {"label": "20h", "value": "20:00:00"},
        {"label": "21h", "value": "21:00:00"},
        {"label": "22h", "value": "22:00:00"},
        {"label": "23h", "value": "23:00:00"}
    ]);
});
