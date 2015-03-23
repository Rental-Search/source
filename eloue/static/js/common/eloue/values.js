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

    EloueCommon.constant("CivilityChoices", {
        "MME": {id: "0", name: "Mme"},
        "MLLE": {id: "1", name: "Mlle"},
        "M": {id: "2", name: "Mr"}
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
        // eloue/static/images/marker_smooth_aligned.png
        unselected: "iVBORw0KGgoAAAANSUhEUgAAABsAAAAbCAYAAACN1PRVAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJ bWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdp bj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6 eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0 NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJo dHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlw dGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAv IiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RS ZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpD cmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNl SUQ9InhtcC5paWQ6N0NFMjAyRUVDMDlDMTFFNEI2MDI5Q0ZCNjFFNUVFNkUiIHhtcE1NOkRvY3Vt ZW50SUQ9InhtcC5kaWQ6N0NFMjAyRUZDMDlDMTFFNEI2MDI5Q0ZCNjFFNUVFNkUiPiA8eG1wTU06 RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDo3Q0UyMDJFQ0MwOUMxMUU0QjYw MjlDRkI2MUU1RUU2RSIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDo3Q0UyMDJFREMwOUMxMUU0 QjYwMjlDRkI2MUU1RUU2RSIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1w bWV0YT4gPD94cGFja2V0IGVuZD0iciI/PrMDAEMAAAGGSURBVHjarJYxSwNBEEY3Z6uIIFqlCcRa sNNCsLpKtEgT0UbBUgsLQX+AhY3aWdhItIxKilSCip0Ea8U0FgpRBNFSzrcyhYg3u3fZgY8hufnm 7SbH7hSSJDGuKJ+vj5Lm0QQqokH0gh7RNTq8n9q6dfUpaDAgJdI2mrG1Sh/b5AStAW2nFUUKKCa1 0KwDZOS5rWuJzx+GYZrUQP0mW9j6hvjdMArLpBrqMfnC+mr0GfHZ2S7qNd2F9e+oMFYzRopNmIil X+rO5kzYqGqw8cCwSQ1WDAwrabDhwLABDfYeGPamwR4Cw9oa7Cow7EKDHQWGHafCOLFvSM1AoKb0 U4+rFfTRJehT+uhnI6u5k5PkKyfI+qrSx33FUHhGquTYoa2viN//8sRQJ9lxoO4J+qkXX/ax4M8M con6Uko6QIZcfSKfJcsws6qUbPr0iXz/DIAHKT/pKc/2g8IkltHzr89PaNHXnAnGDjqkJRndrBb4 7tXX7/WC/PPC7NkbAtBGFl8uWN74FmAAa3N15X3ksJIAAAAASUVORK5CYII=",
        // eloue/static/images/marker_smooth_aligned_selected.png
        selected: "iVBORw0KGgoAAAANSUhEUgAAABsAAAAbCAYAAACN1PRVAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6REQwRTI3REJDMDlFMTFFNDhFQjZBMDdGMUZFODhGOTMiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6REQwRTI3RENDMDlFMTFFNDhFQjZBMDdGMUZFODhGOTMiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDpERDBFMjdEOUMwOUUxMUU0OEVCNkEwN0YxRkU4OEY5MyIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDpERDBFMjdEQUMwOUUxMUU0OEVCNkEwN0YxRkU4OEY5MyIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PvrCJwkAAAGBSURBVHjarJY9SwNBEIb3LpZKEARBSBMwtWIhaGGbKkTBRtFGwdIIdgpib6P+BFE7o8EirYiFIME6kDQWCiYIJpbhfBdGOUJu9iPzwgO53M4+d5fc7gRRFKm/dI7mVUJmwAZYBBkwAVrgDTyBC/A6qHDs+Pn/84jikwUnoAiCvnNThL7CPXAL9kEzabKQEeVBDSwPEPUnoHE1qnOSFcA9SCu3pKmuYCubBpcgpfySovqcjewMjKrhoutPTbI57pk7Jk/zJcrWlWzWONmCsGyJk2WEZVlONiksG+dk38KyL07WEJY1OdmjsOyBk10Jy6452QuoComqNB+7XO2C7pCiH5rHuDbWaSXpeYp6tHLUbbeYClj1uMMu1VVcN88ytQNlS5FxfGiYQL93K2BWtyjMuE8ax76noeVV62amxJw/tJkkiHdXpqD7uqFeI547dFBFm/rQ8Q+wAz5ix+9gy7bYSYY70L/NNoiITXzXtq13eoyxx3mudwiIDlzqvGS++RVgADkXVBKGMOk2AAAAAElFTkSuQmCC",
        // eloue/static/images/marker_large_smooth_aligned.png
        unselectedLarge: "iVBORw0KGgoAAAANSUhEUgAAABsAAAAbCAYAAACN1PRVAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6QkZFRUE0MjlDMDlGMTFFNEJEQUFEMDcwRkRCMzkwRkQiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6QkZFRUE0MkFDMDlGMTFFNEJEQUFEMDcwRkRCMzkwRkQiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDpCRkVFQTQyN0MwOUYxMUU0QkRBQUQwNzBGREIzOTBGRCIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDpCRkVFQTQyOEMwOUYxMUU0QkRBQUQwNzBGREIzOTBGRCIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PqbzffEAAAGwSURBVHjavJY/SMNAFIcvadwEdRAXXap1cBJ00qHg1KlUoUtFFwVHF0HBQdwcXNTZSaqb1VKwIAriWkrninVwUJAiiB0cNP6evMgZknrR5B585O+9L3dJ7p4xdLEqfGIUzIFJMAB6wRswQQewwAcft8AdOAcHN1NbNa+EhocsDrZBhq6L4GGDE7ACaUO+YLpuTIEqmP6jSHA7al9NXK6l/GRpUAJdIpygPCUI025ZAuRBTIQblC8P4bAs2wWdIpqgvDvOBzKGbUVEH+PUs1mhJ3Ikm9AkS5r8w+qIOMn6NMl6SPaiSfZMsltNsgbJrjXJrkh2qEl2ZPIPXY5YVMYKUHGmq2XwGpGoxfm/58Y6zyTvIYsoXw69qruXmCLIhthDypOFqOi3eBa4HCj8U/SVB6IfeSyPG+m/m5FqkCQYBN1cg9hcg8R43+DzVAKctatBrDZPV2OcuAf9HiUARROCkd+6a+EmpXHBaruBzb7P5U2l4sS2beUXAeExFzNynOKBMyrtzYAvfgk8SscPYEG1cSAZevCEzSJ/GMQ8zjWVa7wgwygN5x4tTRCtB2n3KcAAIG1usiPhQ3YAAAAASUVORK5CYII=",
        // eloue/static/images/marker_large_smooth_aligned_selected.png
        selectedLarge: "iVBORw0KGgoAAAANSUhEUgAAABsAAAAbCAYAAACN1PRVAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdpbj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpDcmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNlSUQ9InhtcC5paWQ6REU5OTM3OTlDMDlGMTFFNEJDMzlBNkJEMDlCODc4RTUiIHhtcE1NOkRvY3VtZW50SUQ9InhtcC5kaWQ6REU5OTM3OUFDMDlGMTFFNEJDMzlBNkJEMDlCODc4RTUiPiA8eG1wTU06RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDpERTk5Mzc5N0MwOUYxMUU0QkMzOUE2QkQwOUI4NzhFNSIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDpERTk5Mzc5OEMwOUYxMUU0QkMzOUE2QkQwOUI4NzhFNSIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1wbWV0YT4gPD94cGFja2V0IGVuZD0iciI/PgdTXwUAAAG5SURBVHjavJY/SMNAFMYvadwUdBAXXSouTkJFQYeunaQWulR0UKGji5uguLuom+Ak6NaqiwUncRKkdBasg4OCFKF/Bocav1ff6SlnTDS5Dz6uyeXeLy9N7j3LdV0h1diYFIrG4Hl4Gh6C++EX2Ia7YAd+5eMWfAefwwc9m1cVoZGlgcXhLThN8yK4KOAxvApoVZ2wv12Ygsvw7B9BgtfR+jJuPqXNDBMzGApwTISnNpxBhqcfMIBGOKNuEb6acALAG/kYdyICCY673cmsvj6RwHgtotc4ZTYnzChHsClDsKTNH6wJxQk2YAjWR7C6IdgzwW4NwaoEuzQEuyDYoSHYkY1thD7oUsSgEnHkdrXCe1gUanH89xJDmyTvJO2QQRQvx/E/6xmXgWyIGVKcrCwvuuJZ5Hag+E9QJw5AX+I4mgvpu8soPUgSHoZ7uQdxuQeJ8W+Lz1MLcObVgzged1dhS93Dg5oWgFSDRwHx7hfUhsdLqOaLGPZ/mM4DtPdrc+IXxsACNzOqTgBK+1lvB/zj8/CjcvwAL/ldHAiGDJ4wLPOLQV7AuZrvHi/IY1Qe5y6VJoDWgqx7E2AAhaiFxSb/BWsAAAAASUVORK5CYII=",

        template: [
            '<?xml version="1.0"?>',
            '<svg height="27" width="27" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">',
            '<image xlink:href="data:image/png;base64,{{mapMarker}}" height="27" width="27" y="0" x="0"/>',
            '<text text-anchor="middle" font-family="Open Sans" font-weight="600" y="14" x="13" font-size="10" fill="#FFFFFF">{{markerLabel}}</text>',
            '</svg>'
        ].join('\n')
    })
});
