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
            required_field: "Ce champ est obligatoire."
        });

        $translateProvider.preferredLanguage("fr");
    }]);

});
