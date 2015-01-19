define(["angular-mocks", "eloue/controllers/items/ItemsInfoCtrl"], function () {

    describe("Controller: ItemsInfoCtrl", function () {

        var ItemsInfoCtrl,
            q,
            scope,
            stateParams,
            endpointsMock,
            privateLifeMock,
            fuelMock,
            transmissionMock,
            mileageMock,
            addressesServiceMock,
            categoriesServiceMock,
            picturesServiceMock,
            productsServiceMock,
            phoneNumbersServiceMock,
            simpleServiceResponse = {
                then: function () {
                    return {result: {}};
                }
            };

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {

            q = {
                all: function (obj) {
                    return {then: function () {
                    }}
                }
            };

            endpointsMock = {
                oauth_url: "http://10.0.5.47:8200/oauth2/",
                api_url: "http://10.0.5.47:8200/api/2.0/"
            };

            addressesServiceMock = {
                update: function (address) {
                    console.log("addressesServiceMock:update called with address = " + address);
                    return simpleServiceResponse;
                }
            };

            categoriesServiceMock = {
                getParentCategory: function (category) {
                    console.log("categoriesServiceMock:getParentCategory called with category = " + category);
                    return simpleServiceResponse;
                },
                getRootCategories: function () {
                    console.log("categoriesServiceMock:getRootCategories called ");
                    return simpleServiceResponse;
                },
                getChildCategories: function (parentId) {
                    console.log("categoriesServiceMock:getChildCategories called with parentId = " + parentId);
                    return simpleServiceResponse;
                },
                getCategory: function (categoryId) {
                    console.log("categoriesServiceMock:getCategory called with categoryId = " + categoryId);
                    return simpleServiceResponse;
                }
            };
            picturesServiceMock = {
                savePicture: function (productId, form, successCallback, errorCallback) {
                    console.log("picturesServiceMock:savePicture called with productId = " + productId);
                    return simpleServiceResponse;
                },
                deletePicture: function (pictureId) {
                    return simpleServiceResponse;
                }
            };
            productsServiceMock = {
                getProductDetails: function (id) {
                    console.log("productsServiceMock:getProductDetails called with id = " + id);
                    return simpleServiceResponse;
                },
                updateProduct: function (product) {
                    console.log("productsServiceMock:updateProduct called with product = " + product);
                    return simpleServiceResponse;
                }
            };
            phoneNumbersServiceMock = {
                updatePhoneNumber: function (phoneNumber) {
                    console.log("phoneNumbersServiceMock:updatePhoneNumber called with phoneNumber = " + phoneNumber);
                    return simpleServiceResponse;
                }
            };

            module(function ($provide) {
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("PicturesService", picturesServiceMock);
                $provide.value("ProductsService", productsServiceMock);
                $provide.value("PhoneNumbersService", phoneNumbersServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.showNotification = function(object, action, bool){};
            scope.markListItemAsSelected = function(){};
            scope.initCustomScrollbars = function(){};
            stateParams = {
                id: 1
            };

            spyOn(addressesServiceMock, "update").and.callThrough();
            spyOn(categoriesServiceMock, "getParentCategory").and.callThrough();
            spyOn(categoriesServiceMock, "getRootCategories").and.callThrough();
            spyOn(categoriesServiceMock, "getChildCategories").and.callThrough();
            spyOn(categoriesServiceMock, "getCategory").and.callThrough();
            spyOn(picturesServiceMock, "savePicture").and.callThrough();
            spyOn(picturesServiceMock, "deletePicture").and.callThrough();
            spyOn(productsServiceMock, "getProductDetails").and.callThrough();
            spyOn(productsServiceMock, "updateProduct").and.callThrough();

            ItemsInfoCtrl = $controller('ItemsInfoCtrl', { $q: q, $scope: scope, $stateParams: stateParams, Endpoints: endpointsMock,
                PrivateLife: privateLifeMock, Fuel: fuelMock, Transmission: transmissionMock, Mileage: mileageMock,
                AddressesService: addressesServiceMock, CategoriesService: categoriesServiceMock,
                PicturesService: picturesServiceMock, ProductsService: productsServiceMock});
            expect(productsServiceMock.getProductDetails).toHaveBeenCalledWith(stateParams.id);
            expect(categoriesServiceMock.getRootCategories).toHaveBeenCalled();
        }));

        it("ItemsInfoCtrl should be not null", function () {
            expect(!!ItemsInfoCtrl).toBe(true);
        });

        it("ItemsInfoCtrl:onPictureAdded", function () {
            scope.product = {id: 1};
            scope.onPictureAdded();
        });

        it("ItemsInfoCtrl:updateProduct", function () {
            scope.product = {addressDetails: {} };
            scope.updateProduct();
        });

        it("ItemsInfoCtrl:updateNodeCategories", function () {
            scope.updateNodeCategories();
        });

        it("ItemsInfoCtrl:updateLeafCategories", function () {
            scope.updateLeafCategories();
        });

        it("ItemsInfoCtrl:updateFieldSet", function () {
            var rootCategory = {name: "Automobile"};
            scope.updateFieldSet(rootCategory);
        });

        it("ItemsInfoCtrl:getTimes", function () {
            scope.getTimes();
        });

        it("ItemsInfoCtrl:deletePicture", function () {
            scope.deletePicture();
        });

        it("ItemsInfoCtrl:applyProductDetails", function () {
            var product = {
                category: {
                    id: 1
                }
            };
            scope.applyProductDetails(product);
            expect(categoriesServiceMock.getParentCategory).toHaveBeenCalled();
        });
    });
});