"use strict";
define(["eloue/app", "angular-translate"], function (EloueApp) {

    EloueApp.config(["$translateProvider", function ($translateProvider) {
        // French
        $translateProvider.translations("fr", {

            // Days of week
            Sunday: "Dimanche",
            Monday: "Lundi",
            Tuesday: "Mardi",
            Wednesday: "Mercredi",
            Thursday: "Jeudi",
            Friday: "Vendredi",
            Saturday: "Samedi",

            // Monthes
            January: "Janvier",
            February: "Février",
            March: "Mars",
            April: "Avril",
            May: "Mai",
            June: "Juin",
            July: "Juillet",
            August: "Août",
            September: "Septembre",
            October: "Octobre",
            November: "Novembre",
            December: "Décembre",

            // Preposition
            at: "à",
            Since: "Du",
            to: "au",

            //Booking status
            unpaid: "Impayé",
            authorized: "En attente",
            rejected: "Rejeté",
            pending: "A venir",
            canceled: "Annulé",
            ongoing: "En cours",
            ended: "Terminé",
            closed: "Clôture",
            incident: "Incident",
            refunded: "Remboursé",
            outdated: "Dépassée",

            //Validation errors
            required_field: "Ce champ est obligatoire.",
            zipcode_invalid: "Code postal invalide",
            maxLength10: "Max length is 10 characters",

            //Dashboard form submit messages

            // objects
            address: "Adresse",
            booking: "Réservation",
            comment: "Commentaire",
            item_info: "Annonce",
            item_prices: "Tarifs",
            message: "Message",
            password: "Mot de passe",
            profile: "Profil",
            shipping: "Livraison",
            shipping_point: "Point de livraison",
            sinister: "Sinistre",
            picture: "Photo",

            // actions
            get: "get",
            save: "enregistré",
            update: "mise à jour",
            delete: "supprimé",
            reset: "reset",
            accept: "acceptée",
            reject: "rejetée",
            cancel: "annulée",
            post: "enregistré",
            redirect: "redirigé",
            send: "envoyé",
            upload: "téléchargé",

            // submit statuses
            success: "succeed",
            fail: "failed",

            // No addresses added yet notification
            noAddressTitle: "Pas encore d'adresse renseignée",
            noAddressInfo: "Donner votre adresse rassure le locataire ou le propriétaire et augmente vos chances de louer",
            noAddressButton: "Mettre à jour vos infos",
            informationHasBeenUpdated: "Vous informations ont été mises à jour",

            loadMore: "Charger plus d'éléments"
        });

        $translateProvider.preferredLanguage("fr");
    }]);

});
