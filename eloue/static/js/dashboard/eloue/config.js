define(["eloue/app"],
    function (EloueApp) {
        "use strict";
        
        EloueApp.run(["$translate", "$document", "amMoment", "UtilsService", function($translate, $document, amMoment, UtilsService){
            var locale = UtilsService.locale();
            $translate.use(locale);
            amMoment.changeLocale(locale);
        }]);
        
    });
