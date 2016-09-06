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
                
            SUGGEST_PRO: "Voir {pro_count, plural, "+
                            "one {une annonce d'un professionnel} "+
                            "other {# annonces de professionnels}"+
                        "}",
                                              
            SUGGEST_PART: "Voir {part_count, plural, "+
                            "one {une annonce d'un particulier} "+
                            "other {# annonces de particuliers}"+
                        "}"   
                      
        });
        
        // US English
        $translateProvider.translations("en-US", {
            
            AD_COUNT: '{count, plural, '+
                    '=0 {No ads} '+
                    'one {1 ad} '+
                    'other {# ads}'+
                '} found',
            
            //SEE_PROPART: TODO
            
        });
        
        $translateProvider.preferredLanguage('fr');
        $translateProvider.addInterpolation('$translateMessageFormatInterpolation');
        // $translateProvider.useMessageFormatInterpolation();
        
    }]);

});
