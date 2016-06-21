"use strict";
define(["eloue/app", 
        "angular-translate-interpolation-messageformat"], function (EloueWidgetsApp) {

    EloueWidgetsApp.config(["$translateProvider", function ($translateProvider) {
        
        // French
        $translateProvider.translations("fr", {
            
            AD_COUNT: '{count, plural, '+
                    '=0 {Aucune annonce trouvée} '+
                    'one {1 annonce trouvée} '+
                    'other {# annonces trouvées}'+
                '}',
            
        });
        
        // US English
        $translateProvider.translations("en-US", {
            
            AD_COUNT: '{count, plural, '+
                    '=0 {No ads} '+
                    'one {1 ad} '+
                    'other {# ads}'+
                '} found',
            
        });
        
        $translateProvider.preferredLanguage('fr');
        
        $translateProvider.addInterpolation('$translateMessageFormatInterpolation');
        
    }]);

});
