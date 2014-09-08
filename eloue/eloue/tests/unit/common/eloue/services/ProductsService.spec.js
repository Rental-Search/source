define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: ProductsService", function () {

        var ProductsService,
            addressesServiceMock,
            bookingsMock,
            productsMock,
            categoriesServiceMock,
            phoneNumbersServiceMock,
            picturesServiceMock,
            pricesServiceMock,
            utilsServiceMock,
            usersServiceMock,
            messageThreadsMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            addressesServiceMock = {
                getAddress: function (addressId) {

                }
            };
            bookingsMock = {
                get: function () {
                }
            };
            productsMock = {
                get: function () {
                    return {$promise: {then: function () {
                        return {results: []}
                    }}}
                },
                update: function () {

                }
            };
            categoriesServiceMock = {
                getCategory: function (categoryId) {

                }
            };
            phoneNumbersServiceMock = {
                getPhoneNumber: function (phoneId) {

                }
            };
            picturesServiceMock = {
                getPicturesByProduct: function (productId) {

                }
            };
            pricesServiceMock = {
                getProductPricesPerDay: function (productId) {

                }
            };
            utilsServiceMock = {
                getIdFromUrl: function (url) {
                }
            };
            usersServiceMock = {
                get: function (userId) {

                }
            };
            messageThreadsMock = {
                list: function () {
                }
            };

            module(function ($provide) {
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("Bookings", bookingsMock);
                $provide.value("Products", productsMock);
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("PhoneNumbersService", phoneNumbersServiceMock);
                $provide.value("PicturesService", picturesServiceMock);
                $provide.value("PricesService", pricesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("UsersService", usersServiceMock);
                $provide.value("MessageThreads", messageThreadsMock);
            });
        });

        beforeEach(inject(function (_ProductsService_) {
            ProductsService = _ProductsService_;
            spyOn(addressesServiceMock, "getAddress").andCallThrough();
            spyOn(bookingsMock, "get").andCallThrough();
            spyOn(productsMock, "get").andCallThrough();
            spyOn(productsMock, "update").andCallThrough();
            spyOn(categoriesServiceMock, "getCategory").andCallThrough();
            spyOn(phoneNumbersServiceMock, "getPhoneNumber").andCallThrough();
            spyOn(picturesServiceMock, "getPicturesByProduct").andCallThrough();
            spyOn(pricesServiceMock, "getProductPricesPerDay").andCallThrough();
            spyOn(utilsServiceMock, "getIdFromUrl").andCallThrough();
            spyOn(usersServiceMock, "get").andCallThrough();
            spyOn(messageThreadsMock, "list").andCallThrough();
        }));

        it("ProductsService should be not null", function () {
            expect(!!ProductsService).toBe(true);
        });

        it("ProductsService:getProduct", function () {
            var id = 1;
            ProductsService.getProduct(id);
            expect(productsMock.get).toHaveBeenCalledWith({id: id});
        });

        it("ProductsService:getProductDetails", function () {
            var id = 1;
            ProductsService.getProductDetails(id);
            expect(productsMock.get).toHaveBeenCalledWith({id: id});
        });

        it("ProductsService:getProductsByAddress", function () {
            var addressId = 2;
            ProductsService.getProductsByAddress(addressId);
            expect(productsMock.get).toHaveBeenCalledWith({address: addressId});
        });

        it("ProductsService:getProductsByOwnerAndRootCategory", function () {
            var userId = 3;
            var rootCategoryId = 4;
            ProductsService.getProductsByOwnerAndRootCategory(userId, rootCategoryId);
            var params = {
                owner: userId,
                category__isdescendant: rootCategoryId
            };
            expect(productsMock.get).toHaveBeenCalledWith(params);
        });

        it("ProductsService:updateProduct", function () {
            var product = {id: 2};
            ProductsService.updateProduct(product);
            expect(productsMock.update).toHaveBeenCalledWith({id: product.id}, product);
        });
    });
});