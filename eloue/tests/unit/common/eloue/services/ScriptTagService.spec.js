define(["angular-mocks", "eloue/services/ScriptTagService"], function () {

    describe("Service: ScriptTagService", function () {

        var ScriptTagService,
            window,
            document;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            window = { location: {}, google_trackConversion: function(){}};
            document = [{
                body: {
                    appendChild: function() {

                    }
                },
                createElement: function() {
                return {appendChild: function() {

                }};
            }}];

            module(function ($provide) {
                $provide.value("$window", window);
                $provide.value("$document", document);
            });
        });
        beforeEach(inject(function (_ScriptTagService_) {
            ScriptTagService = _ScriptTagService_;
            spyOn(window, "google_trackConversion").and.callThrough();
            spyOn(document[0], "createElement").and.callThrough();
        }));

        it("ScriptTagService should be not null", function () {
            expect(!!ScriptTagService).toBe(true);
        });

        it("ScriptTagService:loadAdWordsTags", function () {
            var googleConversionLabel = "123";
            ScriptTagService.loadAdWordsTags(googleConversionLabel);
            expect(window.google_trackConversion).toHaveBeenCalledWith({
                google_conversion_id: 1027691277,
                google_conversion_language: "en",
                google_conversion_format: "3",
                google_conversion_color: "ffffff",
                google_conversion_label: googleConversionLabel,
                google_conversion_value: 1.00,
                google_conversion_currency: "EUR",
                google_remarketing_only: false
            });
        });

        it("ScriptTagService:loadPdltrackingScript", function () {
            var currentUserId = 1;
            ScriptTagService.loadPdltrackingScript(currentUserId);
            expect(document[0].createElement).toHaveBeenCalledWith("script");
        });
    });
});