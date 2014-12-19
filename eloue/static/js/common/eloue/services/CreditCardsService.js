"use strict";
define(["../../../common/eloue/commonApp"], function (EloueCommon) {
    /**
     * Service for managing comments.
     */
    EloueCommon.factory("CreditCardsService", [
        "CreditCards",
        function (CreditCards) {
            var creditCardsService = {};

            creditCardsService.saveCard = function (card) {
                return CreditCards.save(card);
            };

            creditCardsService.deleteCard = function (card) {
                return CreditCards.delete({id: card.id});
            };

            return creditCardsService;
        }
    ]);
});
