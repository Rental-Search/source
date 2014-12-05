define(["angular-mocks", "datejs", "eloue/modules/booking/controllers/ProductDetailsCtrl"], function () {

    describe("Controller: ProductDetailsCtrl", function () {

        var ProductDetailsCtrl,
            scope,
            window,
            location,
            endpointsMock,
            civilityChoicesMock,
            productsLoadServiceMock,
            messageThreadsServiceMock,
            productRelatedMessagesLoadServiceMock,
            usersServiceMock,
            authServiceMock,
            addressesServiceMock,
            creditCardsServiceMock,
            bookingsLoadServiceMock,
            bookingsServiceMock,
            phoneNumbersServiceMock,
            categoriesServiceMock,
            utilsServiceMock,
            shippingsServiceMock,
            shippingPointsServiceMock,
            productShippingPointsServiceMock,
            patronShippingPointsServiceMock,
            toDashboardRedirectServiceMock;

        beforeEach(module("EloueApp.BookingModule"));

        beforeEach(function () {
            productsLoadServiceMock = {getProduct: function () {
                return {
                    then: function () {
                        return {result: {}}
                    }
                }
            }, isAvailable: function () {
                return {then: function () {
                    return {result: {}}
                }}
            }};
            messageThreadsServiceMock = {getMessageThread: function () {
                return {
                    then: function () {
                        return {result: {}}
                    }
                }
            }, sendMessage: function () {
                return {
                    then: function () {
                        return {result: {}}
                    }
                }
            }};
            usersServiceMock = {
                get: function (userId) {
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                },
                getMe: function () {
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                },
                updateUser: function(user) {
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };
            authServiceMock = {
                getCookie: function (cookieName) {

                }
            };
            productRelatedMessagesLoadServiceMock = {
                postMessage: function(threadId, senderId, recipientId, text, offerId, productId) {
                    return {
                        then: function () {
                            return {result: {}}
                        }
                    }
                }
            };
            endpointsMock = {
                api_url: "http://10.0.0.111:8000/api/2.0/"
            };

            shippingsServiceMock = {};
            shippingPointsServiceMock = {};
            productShippingPointsServiceMock = {};
            patronShippingPointsServiceMock = {};
            toDashboardRedirectServiceMock = {};
            civilityChoicesMock = {};
            addressesServiceMock = {
                saveAddress:  function(address) {
                    return {$promise: {then: function () {
                        return {result: {}}
                    }}}
                }
            };
            creditCardsServiceMock = {};
            bookingsLoadServiceMock = {
                requestBooking: function(booking) {
                    return {then: function () {
                        return {result: {}}
                    }}
                },
                payForBooking: function(uuid, paymentInfo) {
                    return {then: function () {
                        return {result: {}}
                    }}
                }
            };
            bookingsServiceMock = {
                getBookingsByProduct: function(productId) {
                    return {then: function () {
                        return {result: {}}
                    }}
                }
            };
            phoneNumbersServiceMock = {};
            categoriesServiceMock = {
                getAncestors: function (categoryId) {
                    return {then: function () {
                        return {result: {}}
                    }}
                }
            };
            utilsServiceMock = {};

            module(function ($provide) {
                $provide.value("ProductsLoadService", productsLoadServiceMock);
                $provide.value("MessageThreadsService", messageThreadsServiceMock);
                $provide.value("UserService", usersServiceMock);
                $provide.value("AuthService", authServiceMock);
                $provide.value("Endpoints", endpointsMock);
                $provide.value("CivilityChoices", civilityChoicesMock);
                $provide.value("ProductRelatedMessagesLoadService", productRelatedMessagesLoadServiceMock);
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("CreditCardsService", creditCardsServiceMock);
                $provide.value("BookingsLoadService", bookingsLoadServiceMock);
                $provide.value("BookingsService", bookingsServiceMock);
                $provide.value("PhoneNumbersService", phoneNumbersServiceMock);
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("ShippingsService", shippingsServiceMock);
                $provide.value("ShippingPointsService", shippingPointsServiceMock);
                $provide.value("ProductShippingPointsService", productShippingPointsServiceMock);
                $provide.value("PatronShippingPointsService", patronShippingPointsServiceMock);
                $provide.value("ToDashboardRedirectService", toDashboardRedirectServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            scope.bookingDetails = {
                "fromDate": "",
                "fromHour": "08:00:00",
                "toDate": "",
                "toHour": "08:00:00"
            };
            scope.currentUserPromise = {then: function () {
                return {response: {}}
            }};
            scope.currentUser = {
                id: 111,
                default_address: {
                    country: "FR"
                }
            };
            scope.product = {owner: { id: 111}, category: {name: "Automobile"}};
            window = {location: {href: "location/sdsdfdfsdfsd/sdfsdfsd/sddfsdf/fdff-123"},
                google_trackConversion: function() {

                }};
            location = {};

            spyOn(productsLoadServiceMock, "getProduct").and.callThrough();
            spyOn(productsLoadServiceMock, "isAvailable").and.callThrough();
            spyOn(messageThreadsServiceMock, "getMessageThread").and.callThrough();
            spyOn(messageThreadsServiceMock, "sendMessage").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(usersServiceMock, "getMe").and.callThrough();
            spyOn(usersServiceMock, "updateUser").and.callThrough();
            spyOn(authServiceMock, "getCookie").and.callThrough();
            spyOn(productRelatedMessagesLoadServiceMock, "postMessage").and.callThrough();
            spyOn(addressesServiceMock, "saveAddress").and.callThrough();
            spyOn(bookingsLoadServiceMock, "requestBooking").and.callThrough();
            spyOn(bookingsLoadServiceMock, "payForBooking").and.callThrough();
            spyOn(bookingsServiceMock, "getBookingsByProduct").and.callThrough();
            spyOn(categoriesServiceMock, "getAncestors").and.callThrough();
            spyOn(window, "google_trackConversion").and.callThrough();
            ProductDetailsCtrl = $controller("ProductDetailsCtrl", {
                $scope: scope, $window: window, $location: location, Endpoints: endpointsMock,
                CivilityChoices: civilityChoicesMock,
                ProductsLoadService: productsLoadServiceMock,
                MessageThreadsService: messageThreadsServiceMock,
                ProductRelatedMessagesLoadService: productRelatedMessagesLoadServiceMock,
                UsersService: usersServiceMock,
                AuthService: authServiceMock,
                AddressesService: addressesServiceMock,
                CreditCardsService: creditCardsServiceMock,
                BookingsLoadService: bookingsLoadServiceMock,
                BookingsService: bookingsServiceMock,
                PhoneNumbersService: phoneNumbersServiceMock,
                CategoriesService: categoriesServiceMock,
                UtilsService: utilsServiceMock,
                ShippingsService: shippingsServiceMock,
                ShippingPointsService: shippingPointsServiceMock,
                ProductShippingPointsService: productShippingPointsServiceMock,
                PatronShippingPointsService: patronShippingPointsServiceMock,
                ToDashboardRedirectService: toDashboardRedirectServiceMock
            });
        }));

        it("ProductDetailsCtrl should be not null", function () {
            expect(!!ProductDetailsCtrl).toBe(true);
        });

        it("ProductDetailsCtrl:updatePrice", function () {
            scope.updatePrice();
        });

        it("ProductDetailsCtrl:loadMessageThread", function () {
            scope.loadMessageThread();
        });

        it("ProductDetailsCtrl:getProductIdFromUrl", function () {
            scope.getProductIdFromUrl();
        });

        it("ProductDetailsCtrl:handleResponseErrors", function () {
            scope.handleResponseErrors();
        });

        it("ProductDetailsCtrl:sendMessage", function () {
            scope.sendMessage();
        });

        it("ProductDetailsCtrl:callOwner", function () {
            scope.callOwner();
        });

        it("ProductDetailsCtrl:pointSelected", function () {
            scope.pointSelected();
        });

        it("ProductDetailsCtrl:saveDefaultAddress", function () {
            scope.saveDefaultAddress();
        });

        it("ProductDetailsCtrl:sendBookingRequest", function () {
            scope.sendBookingRequest();
        });

        it("ProductDetailsCtrl:sendBookingRequest(no default address)", function () {
            scope.noAddress = true;
            scope.rootCategory = "automobile";
            scope.sendBookingRequest();
        });

        it("ProductDetailsCtrl:saveCardAndRequestBooking", function () {
            scope.saveCardAndRequestBooking();
        });

        it("ProductDetailsCtrl:requestBooking", function () {
            scope.requestBooking();
        });

        it("ProductDetailsCtrl:payForBooking", function () {
            var booking = { uuid: 1}, paymentInfo = {};
            scope.payForBooking(booking, paymentInfo);
        });

        it("ProductDetailsCtrl:getEventLabel", function () {
            scope.getEventLabel();
        });

        it("ProductDetailsCtrl:getEventLabel (auto)", function () {
            scope.rootCategory = "automobile";
            scope.productCategoryName = "renault";
            expect(scope.getEventLabel()).toEqual("Voiture - " + scope.productCategoryName);
        });
        it("ProductDetailsCtrl:getEventLabel (real estate)", function () {
            scope.rootCategory = "location-saisonniere";
            scope.productCategoryName = "condominium";
            expect(scope.getEventLabel()).toEqual("Logement - " + scope.productCategoryName);
        });

        it("ProductDetailsCtrl:clearCreditCard", function () {
            scope.clearCreditCard();
        });

        it("ProductDetailsCtrl:loadProductCategoryAncestors", function () {
            scope.loadProductCategoryAncestors();
        });

        it("ProductDetailsCtrl:loadPictures", function () {
            scope.loadPictures();
        });

        it("ProductDetailsCtrl:loadPhoneDetails", function () {
            scope.loadPhoneDetails();
        });

        it("ProductDetailsCtrl:loadCreditCards", function () {
            scope.loadCreditCards();
        });

        it("ProductDetailsCtrl:loadProductShippingPoint", function () {
            scope.loadProductShippingPoint();
        });

        it("ProductDetailsCtrl:loadShippingPoints", function () {
            scope.loadShippingPoints();
        });

        it("ProductDetailsCtrl:isAuto", function () {
            scope.isAuto();
        });

        it("ProductDetailsCtrl:isRealEstate", function () {
            scope.isRealEstate();
        });

        it("ProductDetailsCtrl:loadCalendar", function () {
            scope.loadCalendar();
        });

        it("ProductDetailsCtrl:updateCalendar", function () {
            scope.updateCalendar();
        });

        it("ProductDetailsCtrl:selectTab", function () {
            scope.selectTab();
        });

        it("ProductDetailsCtrl:loadAdWordsTags", function () {
            scope.loadAdWordsTags();
        });
    });
});