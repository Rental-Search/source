define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ToDashboardRedirectService", function () {

        var ToDashboardRedirectService,
            window,
            cookies;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            window = { location: {}};
            cookies = {};

            module(function ($provide) {
                $provide.value("$window", window);
                $provide.value("$cookies", cookies);
            });
        });
        beforeEach(inject(function (_ToDashboardRedirectService_) {
            ToDashboardRedirectService = _ToDashboardRedirectService_;
        }));

        it("ToDashboardRedirectService should be not null", function () {
            expect(!!ToDashboardRedirectService).toBe(true);
        });

        it("ToDashboardRedirectService:showPopupAndRedirect", function () {
            var href = "";
            ToDashboardRedirectService.showPopupAndRedirect(href);
        });
    });
});