define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: CategoriesService", function () {

        var CategoriesService,
            categoriesMock,
            utilsServiceMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            categoriesMock = {
                get: function () {
                },
                getChildren: function () {
                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {
                }
            };
            module(function ($provide) {
                $provide.value("Categories", categoriesMock);
                $provide.value("UtilsService", utilsServiceMock);
            });
        });

        beforeEach(inject(function (_CategoriesService_) {
            CategoriesService = _CategoriesService_;
            spyOn(categoriesMock, "get").andCallThrough();
            spyOn(categoriesMock, "getChildren").andCallThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").andCallThrough();
        }));

        it("CategoriesService should be not null", function () {
            expect(!!CategoriesService).toBe(true);
        });
    });
});