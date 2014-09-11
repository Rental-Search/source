define(["../../common/eloue/commonApp"], function (EloueCommon) {

    "use strict";

    /**
     * Web service endpoints.
     */
    EloueCommon.constant("Endpoints", {
        oauth_url: "http://10.0.5.47:8200/oauth2/",
        api_url: "http://10.0.5.47:8200/api/2.0/"
    });

    EloueCommon.constant("Path", {
        templatePrefix: "/templates/" // FIXME: should use /templates/ for local files, and / if HTTP scheme is HTTP/HTTPS
    });

    EloueCommon.constant("ServiceErrors", {
        "invalid_grant": "Bad credentials provided"
    });

    EloueCommon.constant("ActivityType", {
        "ALL": {id: "0", name: "All"},
        "MESSAGE": {id: "1", name: "Messages"},
        "BOOKING": {id: "2", name: "Bookings"},
        "ITEM": {id: "3", name: "Items"},
        "ACCOUNT": {id: "4", name: "Accounts"}
    });

    EloueCommon.constant("Currency", {
        "EUR": {name: "EUR", symbol: "€"},
        "USD": {name: "USD", symbol: "$"},
        "GBP": {name: "GPB", symbol: "£"},
        "JPY": {name: "YEN", symbol: "¥"},
        "XPF": {name: "XPF", symbol: "F"}
    });

    EloueCommon.constant("Unit", {
        "HOUR": {id: 0, name: "heure", description: "1 heure"},
        "DAY": {id: 1, name: "", description: ""},
        "WEEK_END": {id: 2, name: "jour", description: "1 jour"},
        "WEEK": {id: 3, name: "semaine", description: "1 semaine"},
        "TWO_WEEKS": {id: 4, name: "deux semaines", description: "2 semaines"},
        "MONTH": {id: 5, name: "mois", description: "1 mois"},
        "THREE_DAYS": {id: 6, name: "3jours", description: "3 jours"},
        "SEVEN_DAYS": {id: 7, name: "7jours", description: "7 jours"},
        "FIFTEEN_DAYS": {id: 8, name: "15jours", description: "15 jours"},
        "NIGHT": {id: 9, name: "nuit", description: "1 nuit"}
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
    EloueCommon.value("RedirectAfterLogin", { url: "/"});
});