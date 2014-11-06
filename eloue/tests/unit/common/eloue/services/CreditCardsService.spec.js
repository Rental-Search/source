define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: CreditCardsService", function () {

        var CreditCardsService,
            creditCardsMock,
            endpointsMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            creditCardsMock = {
                delete: function () {
                    return {$promise: {}}
                },
                save: function () {
                }
            };
            endpointsMock = {
            };
            module(function ($provide) {
                $provide.value("CreditCards", creditCardsMock);
                $provide.value("Endpoints", endpointsMock);
            });
        });

        beforeEach(inject(function (_CreditCardsService_) {
            CreditCardsService = _CreditCardsService_;
            spyOn(creditCardsMock, "delete").andCallThrough();
            spyOn(creditCardsMock, "save").andCallThrough();
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
