"use strict";
define(["eloue/app",
        "angular-moment",
        "angular-translate-interpolation-messageformat"], function (EloueApp) {
    
    EloueApp.config(["$translateProvider", function ($translateProvider) {
        
        // Datepicker locales from 
        // https://github.com/eternicode/bootstrap-datepicker/tree/master/js/locales
        // TODO remove and use locale files instead
        
        $.fn.datepicker.dates['fr'] = {
            days: ["dimanche", "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi"],
            daysShort: ["dim.", "lun.", "mar.", "mer.", "jeu.", "ven.", "sam."],
            daysMin: ["d", "l", "ma", "me", "j", "v", "s"],
            months: ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"],
            monthsShort: ["janv.", "févr.", "mars", "avril", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."],
            today: "Aujourd'hui",
            monthsTitle: "Mois",
            clear: "Effacer",
            weekStart: 1,
            format: "dd/mm/yyyy"
        };
        
        
        // French
        $translateProvider.translations("fr", {
            
            // Date formats
            DATE:"{{date|date:'dd/MM/yyyy'}}",
            DATETIME:"{{date|date:\"dd/MM/yyyy HH'h'mm\"}}",
            DATE_LONG:"{{date|date:'d/m/Y'}}",
            DATE_LONG_SPACED:"{{date|date:'d F Y'}}",
            
            /**
             * Messages
             */
            MESSAGE_SENT_AT: "Le {{date|amDateFormat:'L'}} à {{date:amDateFormat|'LT'}}",
            
            // Money
            MONEY: "{{value|number:2}} €",
            MONEY_ROUND: "{{value|number}} €",
            
            // Distance
            DISTANCE: "{{value+' km'}}",
            
            // Days of week
            Sunday: "Dimanche",
            Monday: "Lundi",
            Tuesday: "Mardi",
            Wednesday: "Mercredi",
            Thursday: "Jeudi",
            Friday: "Vendredi",
            Saturday: "Samedi",

            // Months
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

            // Booking status
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

            // Validation errors
            required_field: "Ce champ est obligatoire",
            zipcode_invalid: "Code postal invalide",
            email_invalid: "E-mail invalide",
            maxLength10: "Max length is 10 characters",
            
            // submit statuses
            success: "succeed",
            fail: "failed",

            // No addresses added yet notification
            noAddressTitle: "Pas encore d'adresse renseignée",
            noAddressInfo: "Donner votre adresse rassure le locataire ou le propriétaire et augmente vos chances de louer",
            noAddressButton: "Mettre à jour vos infos",

            loadMore: "Charger plus d'éléments",
            getAllMessages: "Afficher les anciens messages",
            
            /**
             * MessageFormat templates
             * 
             * ICU Message Format : http://site.icu-project.org/design/formatting/select
             */
            
            // Durations
            DAYS: 
            "{NUM, plural, "+
                "one {1 jour}"+
                "other {# jours}"+
            "}",
            
            
            
            /**
             * Dashboard form submit messages
             */
            
            // A message with action and object, successful or not
            DASHBOARD_SUBMIT: 
            '{NUM, plural, '+
                'one {{GENDER, select, m{Le } f{La } p{Votre } other{L\'\}}'+
                    '{OBJECT} '+
                    '{SUCCESS, select, true{a été } other{n\'\'a pas été }}'+
                    '{ACTION}'+
                '} '+
                'other {{GENDER, select, p{Vos } other{Les }}'+
                    '{OBJECT} '+
                    '{SUCCESS, select, true{ont été } other{n\'\'ont pas été }}'+
                    '{ACTION}'+
                '}'+
            '}',
            
                
            /**
             * Objects
             * 
             * word|sex|plural
             * 
             * sex:
             * m = male, f = female, 
             * fm, fv = same, but starts with a vowel (+h)
             * p = personal (your/votre/vos)
             * 
             * plural:
             * a number just to indicate if plural 
             *  */ 
            ADDRESS: 'addresse|fv|1',
            BOOKING: 'réservation|m|1',
            COMMENT: 'commentaire|p|1',
            ITEM_INFO: 'annonce|fv|1',
            ITEM_PRICES: 'tarifs|m|10',
            MESSAGE: 'message|p|1',
            PASSWORD: 'mot de passe|m|1',
            PROFILE: 'profil|m|1',
            SHIPPING: 'livraison|f|1',
            SHIPPING_POINT: 'point de livraison|m|1',
            SINISTER: 'sinistre|m|1',
            PICTURE: 'photo|f|1',
            PERSONAL_INFO: 'informations|p|10',
             
            // Actions
            'GET': '{GENDER, select, f{get} fv{get} o{get}}',
            'SAVE': '{NUM, plural, '+
                        'one {{GENDER, select, f{enregistrée} fv{enregistrée} other{enregistré}}} '+
                        'other {{GENDER, select, f{enregistrées} fv{enregistrées} other{enregistrés}}} '+
                    '}',
            'UPDATE': '{NUM, plural, '+
                        'one {{GENDER, select, f{mise} fv{mise} other{mis}}} '+
                        'other {{GENDER, select, f{mises} fv{mises} other{mis}}} '+
                    '} à jour',
            'DELETE': '{GENDER, select, f{supprimée} fv{supprimée} other{supprimé}}',
            'RESET': '{GENDER, select, f{réinitialisée} fv{réinitialisée} other{réinitialisé}}',
            'ACCEPT': '{GENDER, select, f{acceptée} fv{acceptée} other{accepté}}',
            'REJECT': '{GENDER, select, f{rejetée} fv{rejetée} other{rejeté}}',
            'CANCEL': '{GENDER, select, f{annulée} fv{annulée} other{annulé}}',
            'POST': '{GENDER, select, f{enregistrée} fv{enregistrée} other{enregistré}}',
            'REDIRECT': '{GENDER, select, f{redirigée} fv{redirigée} other{redirigé}}',
            'SEND': '{GENDER, select, f{envoyée} fv{envoyée} other{envoyé}}',
            'UPLOAD': '{GENDER, select, f{téléchargée} fv{téléchargée} other{téléchargé}}',
            
            // Maps
            REGION: "FR"
            
        });
        
        // US English
        $translateProvider.translations("en-US", {
            
            // Date formats
            DATE:"{{date|date:'mediumDate'}}",
            DATETIME:"{{date|date:'medium'}}",
            DATE_LONG:"{{date|date:'m/d/Y'}}",
            DATE_LONG_SPACED:"{{date|date:'F d Y'}}",
            
            // Messages
            MESSAGE_SENT_AT: "On {{date|amDateFormat:'L'}} at {{date|amDateFormat:'LT'}}",
            
            // Money
            MONEY: "${{value|number:2}}",
            MONEY_ROUND: "${{value|number}}",
            
            // Distance
            DISTANCE: "{{value+' mi'}}",
            
            // Validation errors
            required_field: "This field is required.",
            zipcode_invalid: "Invalid zipcode",
            email_invalid: "Invalid e-mail",
            maxLength10: "Max length is 10 characters",
            
            // No addresses added yet notification
            noAddressTitle: "No address has been added yet",
            //noAddressInfo: "Donner votre adresse rassure le locataire ou le propriétaire et augmente vos chances de louer",
            noAddressButton: "Update your profile",

            loadMore: "Load more",
            getAllMessages: "Show older messages",
            
            // Hour values // TODO replace with format
            '00h':'0 AM', '01h':'1 AM', '02h':'2 AM','03h':'3 AM','04h':'4 AM','05h':'5 AM',
            '06h':'6 AM', '07h':'7 AM', '08h':'8 AM','09h':'9 AM','10h':'10 AM','11h':'11 AM', 
            '12h':'12 AM', '13h':'1 PM', '14h':'2 PM','15h':'3 PM','16h':'4 PM','17h':'5 PM',
            '18h':'6 PM', '19h':'7 PM', '20h':'8 PM','21h':'9 PM','22h':'10 PM','23h':'11 PM',
            
            // Honorifics
            "Mr":"Mr", "Mme":"Ms", "Mlle":"Ms", 
            
            /**
             * MessageFormat templates
             * 
             * ICU Message Format : http://site.icu-project.org/design/formatting/select
             *  */
            
            DAYS: 
            "{NUM, plural, "+
                "one {1 day}"+
                "other {# days}"+
            "}",
            
            // Message
            DASHBOARD_SUBMIT:
            '{GENDER, select, p{Your } other{}}'+ 
            '{NUM, plural, '+
                'one {'+
                    '{OBJECT} '+
                    '{SUCCESS, select, true{has been } other{could not be }}'+
                    '{ACTION}'+
                '} '+
                'other {'+
                    '{OBJECT} '+
                    '{SUCCESS, select, true{have been } other{could not be }}'+
                    '{ACTION}'+
                '}'+
            '}',
                
            // Objects 
            ADDRESS: 'address|f|1',
            BOOKING: 'booking|m|1',
            COMMENT: 'comment|p|1',
            ITEM_INFO: 'ad|fv|1',
            ITEM_PRICES: 'rates|m|10',
            MESSAGE: 'message|p|1',
            PASSWORD: 'password|m|1',
            PROFILE: 'profile|m|1',
            SHIPPING: 'shipping|f|1',
            SHIPPING_POINT: 'shipping point|m|1',
            SINISTER: 'sinister|m|1',
            PICTURE: 'photo|f|1',
            PERSONAL_INFO: 'personal info|p|1',
             
            // Actions
            'GET': 'retreived',
            'SAVE': 'saved',
            'UPDATE': 'updated',
            'DELETE': 'deleted',
            'RESET': 'reset',
            'ACCEPT': 'accepted',
            'REJECT': 'rejected',
            'CANCEL': 'canceled',
            'POST': 'saved',
            'REDIRECT': 'redirected',
            'SEND': 'sent',
            'UPLOAD': 'uploaded'
            
        });
        
        $translateProvider.preferredLanguage('fr');
        
        $translateProvider.addInterpolation('$translateMessageFormatInterpolation');
        
    }]);
    
    EloueApp.constant('MAP_CONFIG', {
        'fr':{
            region: 'FR'
        },
        'en-US':{
            region: 'US'
        }
    });
    
    EloueApp.constant("angularMomentConfig", {
        
    });

});
