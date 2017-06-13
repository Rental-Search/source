define(["angular-mocks", "eloue/services/CreditCardsService"], function () {

    describe("Service: CreditCardsService", function () {

        var CreditCardsService,
            creditCardsMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            creditCardsMock = {
                delete: function () {
                    return simpleResourceResponse;
                },
                save: function () {
                    return simpleResourceResponse;
                }
            };
            module(function ($provide) {
                $provide.value("CreditCards", creditCardsMock);
            });
        });

        beforeEach(inject(function (_CreditCardsService_) {
            CreditCardsService = _CreditCardsService_;
            spyOn(creditCardsMock, "delete").and.callThrough();
            spyOn(creditCardsMock, "save").and.callThrough();
        }));

        it("CreditCardsService should be not null", function () {
            expect(!!CreditCardsService).toBe(true);
        });

        it("CreditCardsService:saveCard", function () {
            var card = {card_number: "1111222233334444"};
            CreditCardsService.saveCard(card);
            expect(creditCardsMock.save).toHaveBeenCalledWith(card);
        });

        it("CreditCardsService:deleteCard", function () {
            var card = {id: "1"};
            CreditCardsService.deleteCard(card);
            expect(creditCardsMock.delete).toHaveBeenCalledWith({id: card.id});
        });
    });
});
