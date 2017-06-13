define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values",
    "../../../common/eloue/services/UtilsService"], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing categories.
     */
    EloueCommon.factory("CategoriesService", ["$q", "Categories", "UtilsService", function ($q, Categories, UtilsService) {
        var categoriesService = {};

        categoriesService.getCategory = function (categoryId) {
            return Categories.get({id: categoryId, _cache: new Date().getTime()}).$promise;
        };

        categoriesService.getParentCategory = function (category) {
            var parentCategoryId = UtilsService.getIdFromUrl(category.parent);
            return categoriesService.getCategory(parentCategoryId);
        };

        categoriesService.searchByProductTitle = function (query, rootCategoryId) {
            var deferred = $q.defer();

            $.ajax({
                url: "/location/ajouter/category/?q=" + query + "&category=" + rootCategoryId,
                type: "GET",
                success: function (data) {
                    deferred.resolve(data.categories);
                }
            });

            return deferred.promise;
        };

        categoriesService.getRootCategories = function () {
            var deferred = $q.defer();

            Categories.get({parent__isnull: true}).$promise.then(function (result) {
                var total = result.count, pagesCount, catPromises, i;
                if (total <= 10) {
                    deferred.resolve(result.results);
                } else {
                    pagesCount = Math.floor(total / 10) + 1;
                    catPromises = [];

                    for (i = 1; i <= pagesCount; i += 1) {
                        catPromises.push(Categories.get({parent__isnull: true, page: i}).$promise);
                    }

                    $q.all(catPromises).then(
                        function (categories) {
                            var categoryList = [];
                            angular.forEach(categories, function (catPage, index) {
                                angular.forEach(catPage.results, function (value, key) {
                                    categoryList.push({id: value.id, name: value.name})
                                });
                            });
                            deferred.resolve(categoryList);
                        }
                    );

                }
            });

            return deferred.promise;
        };

        categoriesService.getChildCategories = function (parentId) {
            var deferred = $q.defer();
            Categories.getChildren({id: parentId}).$promise.then(function (categories) {
                var categoryList = [];
                angular.forEach(categories, function (value, key) {
                    categoryList.push({id: value.id, name: value.name});
                });
                deferred.resolve(categoryList);
            });
            return deferred.promise;
        };

        categoriesService.getAncestors = function (parentId) {
            var deferred = $q.defer();
            Categories.getAncestors({id: parentId}).$promise.then(function (categories) {
                var categoryList = [];
                angular.forEach(categories, function (value) {
                    categoryList.push({id: value.id, name: value.name});
                });
                deferred.resolve(categoryList);
            });
            return deferred.promise;
        };

        return categoriesService;
    }]);
});
