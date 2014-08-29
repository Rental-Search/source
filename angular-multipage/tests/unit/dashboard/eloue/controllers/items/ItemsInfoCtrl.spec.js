define(["angular-mocks", "eloue/controllers/items/ItemsInfoCtrl"], function () {

    describe("Controller: ItemsInfoCtrl", function () {

        var ItemsInfoCtrl,
            scope,
            stateParams,
            endpointsMock,
            privateLifeMock,
            seatNumberMock,
            doorNumberMock,
            fuelMock,
            transmissionMock,
            mileageMock,
            consumptionMock,
            capacityMock,
            addressesServiceMock,
            categoriesServiceMock,
            picturesServiceMock,
            productsServiceMock,
            phoneNumbersServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            endpointsMock = {
                oauth_url: "http://10.0.5.47:8200/oauth2/",
                api_url: "http://10.0.5.47:8200/api/2.0/"
            };

            addressesServiceMock = {
                update: function (address) {
                    console.log("addressesServiceMock:update called with address = " + address);
                }
            };
            categoriesServiceMock = {
                getParentCategory: function (category) {
                    console.log("categoriesServiceMock:getParentCategory called with category = " + category);
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                },
                getRootCategories: function () {
                    console.log("categoriesServiceMock:getRootCategories called ");
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                },
                getChildCategories: function (parentId) {
                    console.log("categoriesServiceMock:getChildCategories called with parentId = " + parentId);
                    return {then: function () {
                        return {response: {}}
                    }}
                },
                getCategory: function (categoryId) {
                    console.log("categoriesServiceMock:getCategory called with categoryId = " + categoryId);
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };
            picturesServiceMock = {
                savePicture: function (productId, form, successCallback, errorCallback) {
                    console.log("picturesServiceMock:savePicture called with productId = " + productId);
                }
            };
            productsServiceMock = {
                getProductDetails: function (id) {
                    console.log("productsServiceMock:getProductDetails called with id = " + id);
                    return {then: function () {
                        return {response: {}}
                    }}
                },
                updateProduct: function (product) {
                    console.log("productsServiceMock:updateProduct called with product = " + product);
                }
            };
            phoneNumbersServiceMock = {
                updatePhoneNumber: function (phoneNumber) {
                    console.log("phoneNumbersServiceMock:updatePhoneNumber called with phoneNumber = " + phoneNumber);
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
            stateParams = {
                id: 1
            };

            spyOn(addressesServiceMock, "update").andCallThrough();
            spyOn(categoriesServiceMock, "getParentCategory").andCallThrough();
            spyOn(categoriesServiceMock, "getRootCategories").andCallThrough();
            spyOn(categoriesServiceMock, "getChildCategories").andCallThrough();
            spyOn(categoriesServiceMock, "getCategory").andCallThrough();
            spyOn(picturesServiceMock, "savePicture").andCallThrough();
            spyOn(productsServiceMock, "getProductDetails").andCallThrough();
            spyOn(productsServiceMock, "updateProduct").andCallThrough();
            spyOn(phoneNumbersServiceMock, "updatePhoneNumber").andCallThrough();

            ItemsInfoCtrl = $controller('ItemsInfoCtrl', { $scope: scope, $stateParams: stateParams, Endpoints: endpointsMock,
                PrivateLife: privateLifeMock, SeatNumber: seatNumberMock, DoorNumber: doorNumberMock, Fuel: fuelMock,
                Transmission: transmissionMock, Mileage: mileageMock, Consumption: consumptionMock, Capacity: capacityMock,
                AddressesService: addressesServiceMock, CategoriesService: categoriesServiceMock, PicturesService: picturesServiceMock,
                ProductsService: productsServiceMock, PhoneNumbersService: phoneNumbersServiceMock});
            expect(productsServiceMock.getProductDetails).toHaveBeenCalledWith(stateParams.id);
            expect(categoriesServiceMock.getRootCategories).toHaveBeenCalled();
        }));

        it("ItemsInfoCtrl should be not null", function () {
            expect(!!ItemsInfoCtrl).toBe(true);
        });
    });
});