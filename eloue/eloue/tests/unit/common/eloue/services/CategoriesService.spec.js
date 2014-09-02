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
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {
                    var trimmedUrl = url.slice(0, url.length - 1);
                    return trimmedUrl.substring(trimmedUrl.lastIndexOf("/") + 1, url.length);
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

        it("CategoriesService:getCategory", function () {
            var categoryId = 1;
            CategoriesService.getCategory(categoryId);
            expect(categoriesMock.get).toHaveBeenCalledWith({id: categoryId});
        });

        it("CategoriesService:getParentCategory", function () {
            var parentId = "1", category = {parent: "http://10.0.5.47:8200/api/2.0/categories/" + parentId + "/"};
            CategoriesService.getParentCategory(category);
            expect(utilsServiceMock.getIdFromUrl).toHaveBeenCalledWith(category.parent);
            expect(categoriesMock.get).toHaveBeenCalledWith({id: parentId });
        });

        it("CategoriesService:getRootCategories", function () {
            CategoriesService.getRootCategories();
            expect(categoriesMock.get).toHaveBeenCalledWith({parent__isnull: true});
        });

        it("CategoriesService:getChildCategories", function () {
            var parentId = 1;
            CategoriesService.getChildCategories(parentId);
            expect(categoriesMock.getChildren).toHaveBeenCalledWith({id: parentId});
        });
    });
});