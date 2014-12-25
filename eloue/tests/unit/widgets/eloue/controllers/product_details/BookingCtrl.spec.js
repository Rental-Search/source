define(["angular-mocks", "datejs", "eloue/controllers/product_details/BookingCtrl"], function () {

    describe("Controller: BookingCtrl", function () {

        var BookingCtrl,
            scope,
            window,
            location,
            endpointsMock,
            civilityChoicesMock,
            productsServiceMock,
            messageThreadsServiceMock,
            productRelatedMessagesServiceMock,
            usersServiceMock,
            authServiceMock,
            addressesServiceMock,
            creditCardsServiceMock,
            bookingsServiceMock,
            phoneNumbersServiceMock,
            categoriesServiceMock,
            utilsServiceMock,
            shippingsServiceMock,
            shippingPointsServiceMock,
            productShippingPointsServiceMock,
            patronShippingPointsServiceMock,
            toDashboardRedirectServiceMock,
            scriptTagServiceMock;

        beforeEach(module("EloueWidgetsApp"));

        beforeEach(function () {
            productsServiceMock = {getProduct: function () {
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
                getUserToken: function () {

                }
            };
            productRelatedMessagesServiceMock = {
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
            bookingsServiceMock = {
                requestBooking: function(booking) {
                    return {then: function () {
                        return {result: {}}
                    }}
                },
                payForBooking: function(uuid, paymentInfo) {
                    return {
                        then: function () {
                            return {result: {}}
                        }
                    }
                },
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
            scriptTagServiceMock = {
                trackEvent: function (category, action, value) {},
                trackPageView: function () {},
                loadAdWordsTags: function (googleConversionLabel) {}
            };

            module(function ($provide) {
                $provide.value("ProductsService", productsServiceMock);
                $provide.value("MessageThreadsService", messageThreadsServiceMock);
                $provide.value("UserService", usersServiceMock);
                $provide.value("AuthService", authServiceMock);
                $provide.value("Endpoints", endpointsMock);
                $provide.value("CivilityChoices", civilityChoicesMock);
                $provide.value("ProductRelatedMessagesService", productRelatedMessagesServiceMock);
                $provide.value("AddressesService", addressesServiceMock);
                $provide.value("CreditCardsService", creditCardsServiceMock);
                $provide.value("BookingsService", bookingsServiceMock);
                $provide.value("PhoneNumbersService", phoneNumbersServiceMock);
                $provide.value("CategoriesService", categoriesServiceMock);
                $provide.value("UtilsService", utilsServiceMock);
                $provide.value("ShippingsService", shippingsServiceMock);
                $provide.value("ShippingPointsService", shippingPointsServiceMock);
                $provide.value("ProductShippingPointsService", productShippingPointsServiceMock);
                $provide.value("PatronShippingPointsService", patronShippingPointsServiceMock);
                $provide.value("ToDashboardRedirectService", toDashboardRedirectServiceMock);
                $provide.value("ScriptTagService", scriptTagServiceMock);
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
            window = {location: {href: "location/sdsdfdfsdfsd/sdfsdfsd/sddfsdf/fdff-123"}};
            location = {};

            spyOn(productsServiceMock, "getProduct").and.callThrough();
            spyOn(productsServiceMock, "isAvailable").and.callThrough();
            spyOn(messageThreadsServiceMock, "getMessageThread").and.callThrough();
            spyOn(messageThreadsServiceMock, "sendMessage").and.callThrough();
            spyOn(usersServiceMock, "get").and.callThrough();
            spyOn(usersServiceMock, "getMe").and.callThrough();
            spyOn(usersServiceMock, "updateUser").and.callThrough();
            spyOn(authServiceMock, "getUserToken").and.callThrough();
            spyOn(productRelatedMessagesServiceMock, "postMessage").and.callThrough();
            spyOn(addressesServiceMock, "saveAddress").and.callThrough();
            spyOn(bookingsServiceMock, "requestBooking").and.callThrough();
            spyOn(bookingsServiceMock, "payForBooking").and.callThrough();
            spyOn(bookingsServiceMock, "getBookingsByProduct").and.callThrough();
            spyOn(categoriesServiceMock, "getAncestors").and.callThrough();
            spyOn(scriptTagServiceMock, "trackEvent").and.callThrough();
            spyOn(scriptTagServiceMock, "trackPageView").and.callThrough();
            spyOn(scriptTagServiceMock, "loadAdWordsTags").and.callThrough();

            BookingCtrl = $controller("BookingCtrl", {
                $scope: scope, $window: window, $location: location, Endpoints: endpointsMock,
                CivilityChoices: civilityChoicesMock,
                ProductsService: productsServiceMock,
                MessageThreadsService: messageThreadsServiceMock,
                ProductRelatedMessagesService: productRelatedMessagesServiceMock,
                UsersService: usersServiceMock,
                AuthService: authServiceMock,
                AddressesService: addressesServiceMock,
                CreditCardsService: creditCardsServiceMock,
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

        it("BookingCtrl should be not null", function () {
            expect(!!BookingCtrl).toBe(true);
        });

        it("BookingCtrl:updatePrice", function () {
            scope.updatePrice();
        });

        it("BookingCtrl:loadMessageThread", function () {
            scope.loadMessageThread();
        });

        it("BookingCtrl:getProductIdFromUrl", function () {
            scope.getProductIdFromUrl();
        });

        it("BookingCtrl:handleResponseErrors", function () {
            scope.handleResponseErrors();
        });

        it("BookingCtrl:sendMessage", function () {
            scope.sendMessage();
        });

        it("BookingCtrl:callOwner", function () {
            scope.callOwner();
        });

        it("BookingCtrl:pointSelected", function () {
            scope.pointSelected();
        });

        it("BookingCtrl:saveDefaultAddress", function () {
            scope.saveDefaultAddress();
        });

        it("BookingCtrl:sendBookingRequest", function () {
            scope.sendBookingRequest();
        });

        it("BookingCtrl:sendBookingRequest(no default address)", function () {
            scope.noAddress = true;
            scope.rootCategory = "automobile";
            scope.sendBookingRequest();
        });

        it("BookingCtrl:saveCardAndRequestBooking", function () {
            scope.saveCardAndRequestBooking();
        });

        it("BookingCtrl:requestBooking", function () {
            scope.requestBooking();
        });

        it("BookingCtrl:payForBooking", function () {
            var booking = { uuid: 1}, paymentInfo = {};
            scope.payForBooking(booking, paymentInfo);
        });

        it("BookingCtrl:getEventLabel", function () {
            scope.getEventLabel();
        });

        it("BookingCtrl:getEventLabel (auto)", function () {
            scope.isAuto = true;
            scope.productCategoryName = "renault";
            expect(scope.getEventLabel()).toEqual("Voiture - " + scope.productCategoryName);
        });
        it("BookingCtrl:getEventLabel (real estate)", function () {
            scope.isRealEstate = true;
            scope.productCategoryName = "condominium";
            expect(scope.getEventLabel()).toEqual("Logement - " + scope.productCategoryName);
        });

        it("BookingCtrl:clearCreditCard", function () {
            scope.clearCreditCard();
        });

        it("BookingCtrl:loadProductCategoryAncestors", function () {
            scope.loadProductCategoryAncestors();
        });

        it("BookingCtrl:loadPictures", function () {
            scope.loadPictures();
        });

        it("BookingCtrl:loadPhoneDetails", function () {
            scope.loadPhoneDetails();
        });

        it("BookingCtrl:loadCreditCards", function () {
            scope.loadCreditCards();
        });

        it("BookingCtrl:loadProductShippingPoint", function () {
            scope.loadProductShippingPoint();
        });

        it("BookingCtrl:loadShippingPoints", function () {
            scope.loadShippingPoints();
        });
    });
});