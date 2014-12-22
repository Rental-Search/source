define(["angular-mocks", "eloue/services/UtilsService", "datejs"], function () {

    describe("Service: UtilsService", function () {

        var UtilsService,
            filter,
            authServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {

            authServiceMock = {
                getCookie: function(name) {
                    return "U_token"
                }
            };

            module(function ($provide) {
                $provide.value("AuthService", authServiceMock);
            });
        });

        beforeEach(inject(function (_UtilsService_, $filter) {
            filter = $filter;
            spyOn(authServiceMock, "getCookie").and.callThrough();
            UtilsService = _UtilsService_;
        }));

        it("UtilsService should be not null", function () {
            expect(!!UtilsService).toBe(true);
        });

        it("UtilsService:formatDate", function () {
            var date = new Date();
            date.setDate(1);
            date.setMonth(8);
            date.setFullYear(2014);
            var result = UtilsService.formatDate(date, "dd.MM.yyyy");
            expect(result).toEqual("01.09.2014");
        });

        it("UtilsService:getIdFromUrl", function () {
            var id = "1208";
            var url = "http://10.0.5.47:8200/api/2.0/users/" + id + "/";
            var result = UtilsService.getIdFromUrl(url);
            expect(result).toEqual(id);
        });

        it("UtilsService:downloadPdfFile", function () {
            var filename = "voucher.pdf";
            var url = "http://10.0.5.47:8200/api/2.0/shippings/1/";
            UtilsService.downloadPdfFile(url, filename);
            expect(authServiceMock.getCookie).toHaveBeenCalledWith("user_token");
            expect(authServiceMock.getCookie).toHaveBeenCalledWith("csrftoken");
        });
    });
});
