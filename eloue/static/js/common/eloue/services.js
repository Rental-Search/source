"use strict";
define(["../../common/eloue/commonApp", "../../common/eloue/resources", "../../common/eloue/values"],
    function (EloueCommon) {

        /**
         * Service for uploading forms.
         */
        EloueCommon.factory("FormService", ["ServerValidationService", function (ServerValidationService) {
            var formService = {};

            formService.send = function (method, url, $form, successCallback, errorCallback) {
                ServerValidationService.removeErrors();
                $form.ajaxSubmit({
                    type: method,
                    url: url,
                    success: successCallback,
                    error: function(jqXHR, status, message, form){
                        if(jqXHR.status == 400 && !!jqXHR.responseJSON){
                            ServerValidationService.addErrors(jqXHR.responseJSON.message, jqXHR.description, jqXHR.responseJSON.errors);
                        }else{
                            ServerValidationService.addErrors("An error occured!", "An error occured!");
                        }
                        errorCallback.call(null, jqXHR, status, message, form);
                    }
                });
            };

            return formService;
        }]);

        /**
         * Service for managing users.
         */
        EloueCommon.factory("UsersService", ["$q", "Users", "FormService", "Endpoints",
            function ($q, Users, FormService, Endpoints) {
                var usersService = {};

                usersService.get = function (userId, successCallback, errorCallback) {
                    return Users.get({id: userId, _cache: new Date().getTime()}, successCallback, errorCallback);
                };

                usersService.getMe = function (successCallback, errorCallback) {
                    return Users.getMe({_cache: new Date().getTime()}, successCallback, errorCallback);
                };

                usersService.getStatistics = function (userId) {
                    return Users.getStats({id: userId, _cache: new Date().getTime()});
                };

                usersService.sendForm = function (userId, form, successCallback, errorCallback) {
                    // Calculate current user url
                    var currentUserUrl = Endpoints.api_url + "users/" + userId + "/";

                    // Send form to the current user url
                    FormService.send("PUT", currentUserUrl, form, successCallback, errorCallback);
                };

                usersService.resetPassword = function (userId, form) {
                    var resetPasswordUrl = Endpoints.api_url + "users/" + userId + "/reset_password/";
                    var deferred = $q.defer();

                    FormService.send("POST", resetPasswordUrl, form,
                        function (data) {
                            deferred.resolve(data);
                        },
                        function (reason) {
                            deferred.reject(reason);
                        });

                    return deferred.promise;
                };

                usersService.updateUser = function (user) {
                    return Users.update({id: "me"}, user);
                };

                return usersService;
            }
        ]);

        /**
         * Service for managing message threads.
         */
        EloueCommon.factory("MessageThreadsService", [
            "$q",
            "$filter",
            "MessageThreads",
            "Bookings",
            "ProductRelatedMessages",
            "ProductRelatedMessagesService",
            "UsersService",
            "ProductsService",
            "BookingsService",
            "UtilsService",
            function ($q, $filter, MessageThreads, Bookings, ProductRelatedMessages, ProductRelatedMessagesService, UsersService, ProductsService, BookingsService, UtilsService) {
                var messageThreadsService = {};

                messageThreadsService.getMessageThread = function (productId, participantId) {
                    var deferred = $q.defer();
                    var self = this;
                    MessageThreads.list({product: productId, participant: participantId, _cache: new Date().getTime()}).$promise.then(function (result) {
                        var promises = [];
                        angular.forEach(result.results, function (value, key) {
                            angular.forEach(value.messages, function (messageLink, idx) {
                                var messageId = UtilsService.getIdFromUrl(messageLink);
                                promises.push(ProductRelatedMessagesService.getMessage(messageId).$promise);
                            });
                        });
                        $q.all(promises).then(function success(results) {
                            deferred.resolve(results);
                        });
                    });
                    return deferred.promise;
                };

                return messageThreadsService;
            }
        ]);

        /**
         * Service for managing product related messages.
         */
        EloueCommon.factory("ProductRelatedMessagesService", [
            "ProductRelatedMessages",
            "Endpoints",
            function (ProductRelatedMessages, Endpoints) {
                var productRelatedMessagesService = {};

                productRelatedMessagesService.getMessage = function (id) {
                    return ProductRelatedMessages.get({id: id, _cache: new Date().getTime()});
                };

                return productRelatedMessagesService;
            }
        ]);

        /**
         * Service for managing products.
         */
        EloueCommon.factory("ProductsService", [
            "$q",
            "$timeout",
            "AddressesService",
            "Bookings",
            "Products",
            "CategoriesService",
            "PhoneNumbersService",
            "UtilsService",
            "UsersService",
            "MessageThreads",
            "ProductsParseService",
            function ($q, $timeout, AddressesService, Bookings, Products, CategoriesService, PhoneNumbersService, UtilsService, UsersService, MessageThreads, ProductsParseService) {
                var productsService = {};

                productsService.getProductDetails = function (id) {
                    return Products.get({id: id, _cache: new Date().getTime()}).$promise;
                };

                productsService.getProductsByAddress = function (addressId) {
                    var deferred = $q.defer();

                    Products.get({address: addressId, _cache: new Date().getTime()}).$promise.then(function (data) {
                        var promises = [];

                        angular.forEach(data.results, function (value, key) {
                            var productDeferred = $q.defer();

                            var productData = {
                                id: value.id,
                                summary: value.summary,
                                deposit_amount: value.deposit_amount
                            };

                            var productPromises = {};
                            productPromises.stats = Products.getStats({id:  value.id, _cache: new Date().getTime()});

                            // When all data loaded
                            $q.all(productPromises).then(function (results) {
                                var product = ProductsParseService.parseProduct(productData, results.stats, results.ownerStats);
                                productDeferred.resolve(product);
                            });

                            promises.push(productDeferred.promise);
                        });

                        $q.all(promises).then(
                            function (results) {
                                deferred.resolve(results);
                            },
                            function (reasons) {
                                deferred.reject(reasons);
                            }
                        );
                    });

                    return deferred.promise;
                };

                productsService.getProductsByOwnerAndRootCategory = function (userId, rootCategoryId, page) {
                    var deferred = $q.defer();
                    var params = {owner: userId, ordering: "-created_at", _cache: new Date().getTime()};

                    if (rootCategoryId) {
                        params.category__isdescendant = rootCategoryId;
                    }

                    if (page) {
                        params.page = page;
                    }

                    Products.get(params).$promise.then(function (data) {
                        var promises = [];
                        angular.forEach(data.results, function (value, key) {
                            var productDeferred = $q.defer();

                            var product = {
                                id: value.id,
                                summary: value.summary,
                                deposit_amount: value.deposit_amount
                            };

                            if ($.isArray(value.pictures) && (value.pictures.length > 0)) {
                                product.picture = value.pictures[0].image.thumbnail;
                            }

                            if (value.prices && value.prices.length > 0) {
                                product.pricePerDay = value.prices[0].amount;
                            } else {
                                product.pricePerDay = 0;
                            }

                            var subPromises = [];
                            subPromises.push(Products.getStats({id: product.id, _cache: new Date().getTime()}).$promise);
                            $q.all(subPromises).then(
                                function (results) {
                                    product.stats = results[0];
                                    if (product.stats) {
                                        if (product.stats.average_rating) {
                                            product.stats.average_rating = Math.round(product.stats.average_rating);
                                        } else {
                                            product.stats.average_rating = 0;
                                        }
                                    }
                                    productDeferred.resolve(product);
                                },
                                function (reasons) {
                                    productDeferred.reject(reasons);
                                }
                            );

                            promises.push(productDeferred.promise);
                        });

                        $q.all(promises).then(
                            function (results) {
                                deferred.resolve({
                                    list: results,
                                    next: data.next
                                });
                            },
                            function (reasons) {
                                deferred.reject(reasons);
                            }
                        );
                    });

                    return deferred.promise;
                };

                productsService.saveProduct = function (product) {
                    return Products.save(product);
                };

                productsService.updateProduct = function (product) {
                    return Products.update({id: product.id}, product);
                };

                return productsService;
            }
        ]);

        /**
         * Utils service.
         */
        EloueCommon.factory("UtilsService", ["$filter", function ($filter) {
            var utilsService = {};

            utilsService.formatDate = function (date, format) {
                return $filter("date")(date, format);
            };

            utilsService.formatMessageDate = function (dateString, shortFormat, fullFormat) {
                var sentDate = new Date(dateString);
                var nowDate = new Date();
                var dateFormat;

                // If date is today
                if (sentDate.setHours(0, 0, 0, 0) === nowDate.setHours(0, 0, 0, 0)) {
                    dateFormat = shortFormat;
                } else {
                    dateFormat = fullFormat;
                }
                return this.formatDate(sentDate, dateFormat);
            };

            utilsService.getIdFromUrl = function (url) {
                var trimmedUrl = url.slice(0, url.length - 1);
                return trimmedUrl.substring(trimmedUrl.lastIndexOf("/") + 1, url.length);
            };

            utilsService.calculatePeriodBetweenDates = function (startDateString, endDateString) {
                var hourTime = 60 * 60 * 1000;
                var dayTime = 24 * hourTime;

                var startTime = Date.parse(startDateString).getTime();
                var endTime = Date.parse(endDateString).getTime();

                var diffTime = endTime - startTime;

                var periodDays = Math.floor(diffTime / dayTime);
                var periodHours = Math.floor((diffTime - dayTime * periodDays) / hourTime);

                return {
                    period_days: periodDays,
                    period_hours: periodHours
                };
            };

            utilsService.isToday = function(dateStr) {
                var date = Date.parse(dateStr);
                var today = new Date();
                return !!date && date.getDate() == today.getDate() && date.getMonth() == today.getMonth() && date.getFullYear() == today.getFullYear();
            };

            return utilsService;
        }]);

        /**
         * Service for managing bookings.
         */
        EloueCommon.factory("BookingsService", [
            "$q",
            "Bookings",
            "Products",
            "ProductsService",
            "AddressesService",
            "UsersService",
            "PhoneNumbersService",
            "CommentsService",
            "UtilsService",
            function ($q, Bookings, Products, ProductsService, AddressesService, UsersService, PhoneNumbersService, CommentsService, UtilsService) {
                var bookingsService = {};

                bookingsService.getBookingsByProduct = function (productId) {
                    var deferred = $q.defer();
                    var bookingList = [];
                    Bookings.get({product: productId, _cache: new Date().getTime()}).$promise.then(function (data) {

                        angular.forEach(data.results, function (value, key) {
                            var booking = {
                                state: value.state,
                                total_amount: value.total_amount,
                                uuid: value.uuid,
                                start_date: {
                                    day: UtilsService.formatDate(value.started_at, "dd"),
                                    month: UtilsService.formatDate(value.started_at, "MMMM"),
                                    year: UtilsService.formatDate(value.started_at, "yyyy")
                                },
                                end_date: {
                                    day: UtilsService.formatDate(value.ended_at, "dd"),
                                    month: UtilsService.formatDate(value.ended_at, "MMMM"),
                                    year: UtilsService.formatDate(value.ended_at, "yyyy")
                                }
                            };

                            booking.title = value.product.summary;
                            if (jQuery(value.product.pictures).size() > 0) {
                                booking.picture = value.product.pictures[0].image.thumbnail;
                            }
                            bookingList.push(booking);
                        });
                    });
                    deferred.resolve(bookingList);

                    return deferred.promise;
                };

                return bookingsService;
            }
        ]);

        /**
         * Service for managing categories.
         */
        EloueCommon.factory("CategoriesService", ["$q", "Categories", "UtilsService", function ($q, Categories, UtilsService) {
            var categoriesService = {};

            categoriesService.getCategory = function (categoryId) {
                return Categories.get({id: categoryId, _cache: new Date().getTime()});
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
                    var total = result.count;
                    if (total <= 10) {
                        deferred.resolve(result.results);
                    } else {
                        var pagesCount = Math.floor(total / 10) + 1;
                        var catPromises = [];

                        for (var i = 1; i <= pagesCount; i++) {
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
                    angular.forEach(categories, function (value, key) {
                        categoryList.push({id: value.id, name: value.name});
                    });
                    deferred.resolve(categoryList);
                });
                return deferred.promise;
            };

            return categoriesService;
        }]);

        /**
         * Service for managing prices.
         */
        EloueCommon.factory("PricesService", ["Prices", function (Prices) {
            var pricesService = {};

            pricesService.savePrice = function (price) {
                return Prices.save(price);
            };

            pricesService.updatePrice = function (price) {
                return Prices.update({id: price.id}, price);
            };

            return pricesService;
        }]);

        /**
         * Service for managing pictures.
         */
        EloueCommon.factory("PicturesService", ["Pictures", "Endpoints", "FormService", function (Pictures, Endpoints, FormService) {
            var picturesService = {};

            picturesService.savePicture = function (productId, form, successCallback, errorCallback) {
                // Calculate current user url
                var url = Endpoints.api_url + "pictures/";

                // Send form to the url
                FormService.send("POST", url, form, successCallback, errorCallback);
            };

            picturesService.deletePicture = function (pictureId) {
                return Pictures.delete({id: pictureId});
            };

            return picturesService;
        }]);

        /**
         * Service for managing addresses.
         */
        EloueCommon.factory("AddressesService", [
            "$q",
            "Addresses",
            "Endpoints",
            "FormService",
            function ($q, Addresses, Endpoints, FormService) {
                var addressesService = {};

                addressesService.getAddress = function (addressId) {
                    return Addresses.get({id: addressId, _cache: new Date().getTime()});
                };

                addressesService.getAddressesByPatron = function (patronId) {
                    var deferred = $q.defer();

                    Addresses.get({patron: patronId, _cache: new Date().getTime()}).$promise.then(function (result) {
                        var total = result.count;
                        if (total <= 10) {
                            deferred.resolve(result.results);
                        } else {
                            var pagesCount = Math.floor(total / 10) + 1;
                            var adrPromises = [];

                            for (var i = 1; i <= pagesCount; i++) {
                                adrPromises.push(Addresses.get({patron: patronId, _cache: new Date().getTime(), page: i}).$promise);
                            }

                            $q.all(adrPromises).then(
                                function (addresses) {
                                    var addressList = [];
                                    angular.forEach(addresses, function (adrPage, index) {
                                        angular.forEach(adrPage.results, function (value, key) {
                                            addressList.push(value);
                                        });
                                    });
                                    deferred.resolve(addressList);
                                }
                            );

                        }
                    });

                    return deferred.promise;
                };

                addressesService.updateAddress = function (addressId, formData) {
                    var deferred = $q.defer();

                    var currentAddressUrl = Endpoints.api_url + "addresses/" + addressId + "/";
                    FormService.send("POST", currentAddressUrl, formData,
                        function (data) {
                            deferred.resolve(data);
                        },
                        function (reason) {
                            deferred.reject(reason);
                        });

                    return deferred.promise;
                };

                //TODO: leave only 1 update method for addresses
                addressesService.update = function (address) {
                    return Addresses.update({id: address.id}, address);
                };

                addressesService.saveAddress = function (address) {
                    return Addresses.save(address);
                };

                addressesService.deleteAddress = function (addressId) {
                    return Addresses.delete({id: addressId});
                };

                return addressesService;
            }
        ]);

        /**
         * Service for managing phone numbers.
         */
        EloueCommon.factory("PhoneNumbersService", ["PhoneNumbers", function (PhoneNumbers) {
            var phoneNumbersService = {};

            phoneNumbersService.savePhoneNumber = function (phoneNumber) {
                return PhoneNumbers.save(phoneNumber);
            };

            phoneNumbersService.updatePhoneNumber = function (phoneNumber) {
                return PhoneNumbers.update({id: phoneNumber.id}, phoneNumber);
            };

            phoneNumbersService.getPremiumRateNumber = function (phoneNumberId) {
                return PhoneNumbers.getPremiumRateNumber({id: phoneNumberId, _cache: new Date().getTime()});
            };

            return phoneNumbersService;
        }]);

        /**
         * Service for managing comments.
         */
        EloueCommon.factory("CommentsService", [
            "Comments",
            "Endpoints",
            function (Comments, Endpoints) {
                var commentsService = {};

                commentsService.getCommentList = function (bookingUUID) {
                    return Comments.get({_cache: new Date().getTime(), booking: bookingUUID}).$promise;
                };

                commentsService.postComment = function (bookingUUID, comment, rate) {
                    var bookingUrl = Endpoints.api_url + "bookings/" + bookingUUID + "/";
                    return Comments.save({
                        booking: bookingUrl,
                        comment: comment,
                        rate: rate
                    });
                };

                return commentsService;
            }
        ]);

        /**
         * Service for managing sinisters.
         */
        EloueCommon.factory("SinistersService", [
            "Sinisters",
            "Endpoints",
            function (Sinisters, Endpoints) {
                var sinistersService = {};

                sinistersService.getSinisterList = function (bookingUUID) {
                    return Sinisters.get({_cache: new Date().getTime(), booking: bookingUUID}).$promise;
                };

                return sinistersService;
            }
        ]);

        /**
         * Service for managing shippings.
         */
        EloueCommon.factory("ShippingsService", [
            "Shippings",
            "Endpoints",
            function (Shippings, Endpoints) {
                var shippingsService = {};

                shippingsService.getByBooking = function (uuid) {
                    return Shippings.get({_cache: new Date().getTime(), booking: uuid}).$promise;
                };

                shippingsService.saveShipping = function (shipping) {
                    return Shippings.save(shipping);
                };

                return shippingsService;
            }
        ]);


        /**
         * Service for managing shipping points.
         */
        EloueCommon.factory("ShippingPointsService", [
            "ShippingPoints",
            "Products",
            "Endpoints",
            function (ShippingPoints, Products, Endpoints) {
                var shippingPointsService = {};

                shippingPointsService.searchDepartureShippingPointsByAddress = function(address) {
                   return shippingPointsService.searchShippingPointsByAddress(address, 1);
                };

                shippingPointsService.searchDepartureShippingPointsByCoordinates = function(lat, lng) {
                    return shippingPointsService.searchShippingPointsByCoordinates(lat, lng, 1);
                };

                shippingPointsService.searchArrivalShippingPointsByAddress = function(address) {
                    return shippingPointsService.searchShippingPointsByAddress(address, 2);
                };

                shippingPointsService.searchArrivalShippingPointsByCoordinates = function(lat, lng) {
                    return shippingPointsService.searchShippingPointsByCoordinates(lat, lng, 2);
                };

                shippingPointsService.searchArrivalShippingPointsByCoordinatesAndProduct = function(lat, lng, productId) {
                    return Products.getShippingPoints({id: productId, lat: lat, lng: lng, search_type: 2, _cache: new Date().getTime()}).$promise;
                };

                shippingPointsService.searchArrivalShippingPointsByAddressAndProduct = function(address, productId) {
                    return Products.getShippingPoints({id: productId, address: address, search_type: 2, _cache: new Date().getTime()}).$promise;
                };

                shippingPointsService.searchShippingPointsByCoordinates = function(lat, lng, searchType) {
                    return ShippingPoints.get({lat: lat, lng: lng, search_type: searchType, _cache: new Date().getTime()}).$promise;
                };

                shippingPointsService.searchShippingPointsByAddress = function(address, searchType) {
                    return ShippingPoints.get({address: address, search_type: searchType, _cache: new Date().getTime()}).$promise;
                };

                return shippingPointsService;
            }
        ]);

        /**
         * Service for managing product shipping points.
         */
        EloueCommon.factory("ProductShippingPointsService", [
            "ProductShippingPoints",
            "Endpoints",
            function (ProductShippingPoints, Endpoints) {
                var productShippingPointsService = {};

                productShippingPointsService.saveShippingPoint = function (shippingPoint) {
                    return ProductShippingPoints.save(shippingPoint);
                };

                productShippingPointsService.deleteShippingPoint = function (shippingPointId) {
                    return ProductShippingPoints.delete({id: shippingPointId});
                };

                productShippingPointsService.getByProduct = function (productId) {
                    return ProductShippingPoints.get({_cache: new Date().getTime(), product: productId}).$promise;
                };

                return productShippingPointsService;
            }
        ]);

        /**
         * Service for managing patron shipping points.
         */
        EloueCommon.factory("PatronShippingPointsService", [
            "PatronShippingPoints",
            "Endpoints",
            function (PatronShippingPoints, Endpoints) {
                var patronShippingPointsService = {};

                patronShippingPointsService.saveShippingPoint = function (shippingPoint) {
                    return PatronShippingPoints.save(shippingPoint);
                };

                patronShippingPointsService.getByPatronAndBooking = function (userId, bookingId) {
                    return PatronShippingPoints.get({_cache: new Date().getTime(), patron: userId, booking: bookingId}).$promise;
                };

                return patronShippingPointsService;
            }
        ]);

        /**
         * Service for managing comments.
         */
        EloueCommon.factory("CreditCardsService", [
            "CreditCards",
            "Endpoints",
            function (CreditCards, Endpoints) {
                var creditCardsService = {};

                creditCardsService.saveCard = function (card) {
                    return CreditCards.save(card);
                };

                creditCardsService.deleteCard = function (card) {
                    return CreditCards.delete({id: card.id});
                };

                return creditCardsService;
            }
        ]);

        /**
         * Service for parsing bookings.
         */
        EloueCommon.factory("BookingsParseService", [
            "UtilsService",
            function (UtilsService) {
                var bookingsParseService = {};

                bookingsParseService.parseBookingListItem = function (bookingData, productData, picturesDataArray) {
                    var bookingResult = angular.copy(bookingData);

                    // Parse dates
                    bookingResult.start_date = {
                        day: UtilsService.formatDate(bookingResult.started_at, "dd"),
                        month: UtilsService.formatDate(bookingResult.started_at, "MMMM"),
                        year: UtilsService.formatDate(bookingResult.started_at, "yyyy")
                    };

                    bookingResult.end_date = {
                        day: UtilsService.formatDate(bookingResult.ended_at, "dd"),
                        month: UtilsService.formatDate(bookingResult.ended_at, "MMMM"),
                        year: UtilsService.formatDate(bookingResult.ended_at, "yyyy")
                    };

                    // Parse product
                    bookingResult.product = productData;

                    // Parse pictures
                    if (angular.isArray(picturesDataArray) && picturesDataArray.length > 0) {
                        bookingResult.picture = picturesDataArray[0].image.thumbnail;
                    }

                    return bookingResult;
                };

                bookingsParseService.parseBooking = function (bookingData) {
                    var bookingResult = angular.copy(bookingData);

                    // Parse dates
                    bookingResult.start_date = {
                        week_day: UtilsService.formatDate(bookingResult.started_at, "EEEE"),
                        day: UtilsService.formatDate(bookingResult.started_at, "dd"),
                        month: UtilsService.formatDate(bookingResult.started_at, "MMMM"),
                        year: UtilsService.formatDate(bookingResult.started_at, "yyyy")
                    };

                    bookingResult.end_date = {
                        week_day: UtilsService.formatDate(bookingResult.ended_at, "EEEE"),
                        day: UtilsService.formatDate(bookingResult.ended_at, "dd"),
                        month: UtilsService.formatDate(bookingResult.ended_at, "MMMM"),
                        year: UtilsService.formatDate(bookingResult.ended_at, "yyyy")
                    };

                    bookingResult.start_time = UtilsService.formatDate(bookingResult.started_at, "HH'h'mm");
                    bookingResult.end_time = UtilsService.formatDate(bookingResult.ended_at, "HH'h'mm");

                    // Parse period
                    var period = UtilsService.calculatePeriodBetweenDates(bookingResult.started_at, bookingResult.ended_at);

                    bookingResult.period_days = period.period_days;
                    bookingResult.period_hours = period.period_hours;

                    return bookingResult;
                };

                return bookingsParseService;
            }
        ]);

        /**
         * Service for parsing products.
         */
        EloueCommon.factory("ProductsParseService", [function () {
            var productsParseService = {};

            productsParseService.parseProduct = function (productData, statsData, ownerStatsData) {
                var productResult = angular.copy(productData);

                productResult.stats = statsData;
                if (productResult.stats) {
                    if (productResult.stats && productResult.stats.average_rating) {
                        productResult.stats.average_rating = Math.round(productResult.stats.average_rating);
                    } else {
                        productResult.stats.average_rating = 0;
                    }
                }

                if (!!ownerStatsData) {
                    productResult.ownerStats = ownerStatsData;
                }

                return productResult;
            };

            return productsParseService;
        }]);

        /**
         * Service for parsing comments.
         */
        EloueCommon.factory("CommentsParseService", [function () {
            var commentsParseService = {};

            commentsParseService.parseComment = function (commentData, authorData) {
                var commentResult = angular.copy(commentData);

                // Parse author
                if (!!authorData) {
                    commentResult.author = authorData;
                }

                return commentResult;
            };

            return commentsParseService;
        }]);

        /**
         * Service for managing bookings.
         */
        EloueCommon.factory("BookingsLoadService", [
            "$q",
            "Bookings",
            "UtilsService",
            "BookingsParseService",
            "ProductsLoadService",
            "MessageThreadsService",
            function ($q, Bookings, UtilsService, BookingsParseService, ProductsLoadService, MessageThreadsService) {
                var bookingsLoadService = {};

                bookingsLoadService.getBookingList = function (author, state, borrowerId, ownerId, page) {
                    var deferred = $q.defer();
                    var params = {
                        page: page,
                        author: author,
                        ordering: "-created_at",
                        _cache: new Date().getTime()
                    };
                    if (!!state) {
                        params.state = state;
                    }
                    if (!!borrowerId) {
                        params.borrower = borrowerId;
                    }
                    if (!!ownerId) {
                        params.owner = ownerId;
                    }

                    // Load bookings
                    Bookings.get(params).$promise.then(function (bookingListData) {
                        var bookingListPromises = [];

                        // For each booking
                        angular.forEach(bookingListData.results, function (bookingData, key) {
                            var bookingDeferred = $q.defer();

                            var booking = BookingsParseService.parseBookingListItem(bookingData, bookingData.product, bookingData.product.pictures);
                            bookingDeferred.resolve(booking);

                            bookingListPromises.push(bookingDeferred.promise);
                        });

                        $q.all(bookingListPromises).then(function (bookingList) {
                            deferred.resolve(
                                {
                                    list: bookingList,
                                    next: bookingListData.next
                                });
                        });
                    });

                    return deferred.promise;
                };

                bookingsLoadService.getBooking = function (bookingUUID) {
                    var deferred = $q.defer();

                    // Load booking
                    Bookings.get({uuid: bookingUUID, _cache: new Date().getTime()}).$promise.then(function (bookingData) {
                        var booking = BookingsParseService.parseBooking(bookingData);
                        if (jQuery(bookingData.product.pictures).size() > 0) {
                            booking.product.picture = bookingData.product.pictures[0].image.thumbnail;
                        }
                        deferred.resolve(booking);
                    });

                    return deferred.promise;
                };

                bookingsLoadService.getBookingDetails = function (bookingUUID) {
                    var deferred = $q.defer();

                    // Load booking
                    this.getBooking(bookingUUID).then(function (booking) {
                        MessageThreadsService.getMessageThread(booking.product.id, booking.borrower.id).then(function (threads) {
                            if (threads && threads.length > 0) {
                                booking.lastThreadId = UtilsService.getIdFromUrl(threads[threads.length - 1].thread);
                            }
                            console.log(booking);
                            deferred.resolve(booking);
                        });
                    });

                    return deferred.promise;
                };

                bookingsLoadService.acceptBooking = function (uuid) {
                    return Bookings.accept({uuid: uuid}, {uuid: uuid});
                };

                bookingsLoadService.cancelBooking = function (uuid) {
                    return Bookings.cancel({uuid: uuid}, {uuid: uuid});
                };

                bookingsLoadService.rejectBooking = function (uuid) {
                    return Bookings.reject({uuid: uuid}, {uuid: uuid});
                };

                bookingsLoadService.postIncident = function (uuid, description) {
                    return Bookings.incident({uuid: uuid}, {description: description});
                };

                bookingsLoadService.getBookingByProduct = function (productId) {
                    var deferred = $q.defer();

                    // Load all bookings for this product
                    Bookings.get({product: productId, _cache: new Date().getTime()}).$promise.then(function (bookingListData) {
                        var bookingsCount = bookingListData.results.length;
                        var booking = null;

                        if (bookingsCount > 0) {
                            var bookingData = bookingListData.results[bookingsCount - 1];
                            booking = BookingsParseService.parseBooking(bookingData);
                        }

                        deferred.resolve(booking);
                    });

                    return deferred.promise;
                };

                bookingsLoadService.requestBooking = function (booking) {
                    return Bookings.save(booking).$promise;
                };

                bookingsLoadService.payForBooking = function (uuid, paymentInfo) {
                    return Bookings.pay({uuid: uuid}, paymentInfo).$promise;
                };
                return bookingsLoadService;
            }
        ]);

        /**
         * Service for managing products.
         */
        EloueCommon.factory("ProductsLoadService", [
            "$q",
            "Products",
            "CheckAvailability",
            "AddressesService",
            "UsersService",
            "PhoneNumbersService",
            "UtilsService",
            "ProductsParseService",
            function ($q, Products, CheckAvailability, AddressesService, UsersService, PhoneNumbersService, UtilsService, ProductsParseService) {
                var productsLoadService = {};

                productsLoadService.getProduct = function (productId, loadProductStats, loadOwnerStats) {
                    var deferred = $q.defer();

                    // Load product
                    Products.get({id: productId, _cache: new Date().getTime()}).$promise.then(function (productData) {
                        var productPromises = {};

                        if (loadProductStats) {
                            productPromises.stats = Products.getStats({id: productId, _cache: new Date().getTime()});
                        }
                            if (loadOwnerStats) {
                                productPromises.ownerStats = UsersService.getStatistics(productData.owner.id).$promise;
                            }
                        // When all data loaded
                        $q.all(productPromises).then(function (results) {
                            var product = ProductsParseService.parseProduct(productData, results.stats, results.ownerStats);
                            deferred.resolve(product);
                        });
                    });

                    return deferred.promise;
                };

                productsLoadService.getAbsoluteUrl = function(id) {
                    return Products.getAbsoluteUrl({id: id,cache: new Date().getTime()});
                };

                productsLoadService.isAvailable = function (id, startDate, endDate, quantity) {
                    return CheckAvailability.get({id: id, started_at: startDate, ended_at: endDate, quantity: quantity}).$promise;
                };

                return productsLoadService;
            }
        ]);

        /**
         * Service for managing comments.
         */
        EloueCommon.factory("CommentsLoadService", [
            "$q",
            "Comments",
            "Endpoints",
            "UsersService",
            "UtilsService",
            "CommentsParseService",
            function ($q, Comments, Endpoints, UsersService, UtilsService, CommentsParseService) {
                var commentsLoadService = {};

                commentsLoadService.getCommentList = function (bookingUUID) {
                    var deferred = $q.defer();
                    var commentListPromises = [];

                    // Load comments
                    Comments.get({booking: bookingUUID, _cache: new Date().getTime()}).$promise.then(function (commentListData) {
                        angular.forEach(commentListData.results, function (commentData, key) {
                            var commentDeferred = $q.defer();

                            // Get author id
                            var authorId = UtilsService.getIdFromUrl(commentData.author);
                            // Load author
                            UsersService.get(authorId).$promise.then(function (authorData) {
                                var comment = CommentsParseService.parseComment(commentData, authorData);
                                commentDeferred.resolve(comment);
                            });

                            commentListPromises.push(commentDeferred.promise);
                        });

                        $q.all(commentListPromises).then(function (results) {
                            deferred.resolve(results);
                        });
                    });

                    return deferred.promise;
                };

                commentsLoadService.postComment = function (bookingUUID, comment, rate) {
                    var bookingUrl = Endpoints.api_url + "bookings/" + bookingUUID + "/";
                    return Comments.save({
                        booking: bookingUrl,
                        comment: comment,
                        rate: rate
                    });
                };

                return commentsLoadService;
            }
        ]);

        /**
         * Service for managing message threads.
         */
        EloueCommon.factory("MessageThreadsLoadService", [
            "$q",
            "MessageThreads",
            "UsersService",
            "ProductRelatedMessagesService",
            "UtilsService",
            "MessageThreadsParseService",
            "ProductRelatedMessagesLoadService",
            "ProductsLoadService",
            function ($q, MessageThreads, UsersService, ProductRelatedMessagesService, UtilsService, MessageThreadsParseService, ProductRelatedMessagesLoadService, ProductsLoadService) {
                var messageThreadsLoadService = {};

                messageThreadsLoadService.getMessageThreadList = function (loadSender, loadLastMessage, page) {
                    var deferred = $q.defer();

                    // Load message threads
                    MessageThreads.get({page: page, ordering: "-last_message__sent_at", _cache: new Date().getTime()}).$promise.then(function (messageThreadListData) {
                        var messageThreadListPromises = [];

                        // For each message thread
                        angular.forEach(messageThreadListData.results, function (messageThreadData, key) {
                            var messageThreadDeferred = $q.defer();
                            var messageThreadPromises = {};

                            // Get sender id
                            if (loadSender) {
                                var senderId = UtilsService.getIdFromUrl(messageThreadData.sender);
                                // Load sender
                                messageThreadPromises.sender = UsersService.get(senderId).$promise;
                            }

                            // Get last message id
                            if (loadLastMessage && !!messageThreadData.last_message) {
                                var lastMessageId = UtilsService.getIdFromUrl(messageThreadData.last_message);
                                // Load last message
                                messageThreadPromises.last_message = ProductRelatedMessagesService.getMessage(lastMessageId).$promise;
                            }

                            // When all data loaded
                            $q.all(messageThreadPromises).then(function (messageThreadResults) {
                                var messageThread = MessageThreadsParseService.parseMessageThreadListItem(messageThreadData,
                                    messageThreadResults.sender, messageThreadResults.last_message);
                                messageThreadDeferred.resolve(messageThread);
                            });

                            messageThreadListPromises.push(messageThreadDeferred.promise);
                        });

                        $q.all(messageThreadListPromises).then(function (messageThreadList) {
                            deferred.resolve({
                                list: messageThreadList,
                                next: messageThreadListData.next
                            });
                        });
                    });

                    return deferred.promise;
                };

                messageThreadsLoadService.getMessageThread = function (threadId) {
                    var deferred = $q.defer();

                    // Load message thread
                    MessageThreads.get({id: threadId, _cache: new Date().getTime()}).$promise.then(function (messageThreadData) {
                        var messageThreadPromises = {};

                        // Load messages
                        var messagesPromises = [];
                        angular.forEach(messageThreadData.messages, function (messageUrl, key) {
                            // Get message id
                            var messageId = UtilsService.getIdFromUrl(messageUrl);
                            // Load message
                            messagesPromises.push(ProductRelatedMessagesLoadService.getMessageListItem(messageId));
                        });
                        // When all messages loaded
                        messageThreadPromises.messages = $q.all(messagesPromises);

                        // Get product id
                        if (messageThreadData.product) {
                            var productId = UtilsService.getIdFromUrl(messageThreadData.product);
                            messageThreadPromises.product = ProductsLoadService.getProduct(productId, true, true);
                        }

                        $q.all(messageThreadPromises).then(function (results) {
                            var messageThread = MessageThreadsParseService.parseMessageThread(messageThreadData, results.messages, results.product);
                            deferred.resolve(messageThread);
                        });
                    });

                    return deferred.promise;
                };

                messageThreadsLoadService.getUsersRoles = function (messageThread, currentUserId) {
                    var senderId = UtilsService.getIdFromUrl(messageThread.sender);
                    var recipientId = UtilsService.getIdFromUrl(messageThread.recipient);

                    var result = {
                        senderId: currentUserId
                    };

                    if (senderId == currentUserId) {
                        result.recipientId = recipientId;
                    } else {
                        result.recipientId = senderId;
                    }

                    return result;
                };

                return messageThreadsLoadService;
            }
        ]);

        /**
         * Service for parsing message threads.
         */
        EloueCommon.factory("MessageThreadsParseService", [
            "UtilsService",
            function (UtilsService) {
                var messageThreadsParseService = {};

                messageThreadsParseService.parseMessageThreadListItem = function (messageThreadData, senderData, lastMessageData) {
                    var messageThreadResult = angular.copy(messageThreadData);

                    // Parse sender
                    if (!!senderData) {
                        messageThreadResult.sender = senderData;
                    }

                    // Parse last message
                    if (!!lastMessageData) {
                        messageThreadResult.last_message = lastMessageData;
                        // if the creation date of the last message is the current day display only the hour
                        // if the creation date of the last message is before the current day display the date and not the hour
                        if (UtilsService.isToday(lastMessageData.sent_at)) {
                            messageThreadResult.last_message.sent_at = UtilsService.formatDate(lastMessageData.sent_at, "HH'h'mm");
                        } else {
                            messageThreadResult.last_message.sent_at = UtilsService.formatDate(lastMessageData.sent_at, "dd.MM.yyyy");
                        }
                    }

                    return messageThreadResult;
                };

                messageThreadsParseService.parseMessageThread = function (messageThreadData, messagesDataArray, productData) {
                    var messageThreadResult = angular.copy(messageThreadData);

                    // Parse messages
                    if (!!messagesDataArray) {
                        messageThreadResult.messages = messagesDataArray;
                        angular.forEach(messageThreadResult.messages, function (message, key) {
                            message.sent_at = UtilsService.formatDate(message.sent_at, "dd.MM.yyyy HH'h'mm");
                        });
                    }

                    // Parse product
                    if (!!productData) {
                        messageThreadResult.product = productData;
                    }

                    return messageThreadResult;
                };
                return messageThreadsParseService;
            }
        ]);

        /**
         * Service for managing product related messages.
         */
        EloueCommon.factory("ProductRelatedMessagesLoadService", [
            "$q",
            "ProductRelatedMessages",
            "Endpoints",
            "MessageThreads",
            "UsersService",
            "UtilsService",
            "ProductRelatedMessagesParseService",
            function ($q, ProductRelatedMessages, Endpoints, MessageThreads, UsersService, UtilsService, ProductRelatedMessagesParseService) {
                var productRelatedMessagesLoadService = {};

                productRelatedMessagesLoadService.getMessage = function (messageId) {
                    return ProductRelatedMessages.get({id: messageId, _cache: new Date().getTime()}).$promise;
                };

                productRelatedMessagesLoadService.getMessageListItem = function (messageId) {
                    var deferred = $q.defer();

                    this.getMessage(messageId).then(function (messageData) {
                        // Get sender id
                        var senderId = UtilsService.getIdFromUrl(messageData.sender);
                        // Load sender
                        UsersService.get(senderId).$promise.then(function (senderData) {
                            var message = ProductRelatedMessagesParseService.parseMessage(messageData, senderData);
                            deferred.resolve(message);
                        });

                    });

                    return deferred.promise;
                };

                productRelatedMessagesLoadService.postMessage = function (threadId, senderId, recipientId, text, offerId, productId) {
                    var threadDef = $q.defer();
                    var self = this;
                    if (!threadId) {
                        var messageThread = {
                            sender: Endpoints.api_url + "users/" + senderId + "/",
                            recipient: Endpoints.api_url + "users/" + recipientId + "/",
                            product: Endpoints.api_url + "products/" + productId + "/",
                            subject: "Question",
                            messages: []
                        };
                        MessageThreads.save({}, messageThread, function (response) {
                            threadDef.resolve(response.id);
                        });
                    } else {
                        threadDef.resolve(threadId);
                    }
                    var deferred = $q.defer();
                    threadDef.promise.then(function (result) {
                        var message = {
                            thread: Endpoints.api_url + "messagethreads/" + result + "/",
                            sender: Endpoints.api_url + "users/" + senderId + "/",
                            recipient: Endpoints.api_url + "users/" + recipientId + "/",
                            body: (!!text) ? text : "",
                            offer: (!!offerId) ? Endpoints.api_url + "bookings/" + offerId + "/" : null
                        };
                        ProductRelatedMessages.save({}, message, function (response) {
                            var senderId = UtilsService.getIdFromUrl(response.sender);
                            UsersService.get(senderId).$promise.then(function (result) {
                                response.sender = result;
                                deferred.resolve(response);
                            });
                        });
                    });
                    return deferred.promise;
                };

                productRelatedMessagesLoadService.updateMessage = function (message) {
                    return ProductRelatedMessages.update({id: message.id}, message);
                };


                return productRelatedMessagesLoadService;
            }
        ]);

        /**
         * Service for parsing product related messages.
         */
        EloueCommon.factory("ProductRelatedMessagesParseService", [function () {
            var productRelatedMessagesParseService = {};

            productRelatedMessagesParseService.parseMessage = function (messageData, senderData) {
                var messageResults = angular.copy(messageData);

                // Parse sender
                if (!!senderData) {
                    messageResults.sender = senderData;
                }

                return messageResults;
            };

            return productRelatedMessagesParseService;
        }]);

        EloueCommon.factory("AuthService", ["$q", "$window", "Endpoints", "AuthConstants", "RedirectAfterLogin", "Registration", "FormService", function ($q, $window, Endpoints, AuthConstants, RedirectAfterLogin, Registration, FormService) {
            return {

                /**
                 * Sign in user with provided credentials.
                 * @param credentials user credentials
                 * @returns Signed in user object
                 * @param successCallback success callback function
                 * @param errorCallback error callback function
                 */
                login: function (credentials, successCallback, errorCallback) {
                    $.ajax({
                        url: Endpoints.oauth_url + "access_token/",
                        type: "POST",
                        data: {
                            client_id: AuthConstants.clientId,
                            client_secret: AuthConstants.clientSecret,
                            grant_type: AuthConstants.grantType,
                            username: credentials.username,
                            password: credentials.password
                        },
                        success: successCallback,
                        error: errorCallback
                    });
                },

                /**
                 * Remove user token.
                 */
                clearUserData: function () {
                    document.cookie = "user_token=;expires=" + new Date(0).toGMTString() + ";path=/";
                },

                /**
                 * Redirect to attempted URL.
                 */
                redirectToAttemptedUrl: function () {
                    $window.location.href = RedirectAfterLogin.url;
                },

                /**
                 * Save URL that user attempts to access.
                 */
                saveAttemptUrl: function () {
                    RedirectAfterLogin.url = $window.location.href;
                },

                /**
                 * Sends password reset request.
                 * @param form form
                 * @param successCallback success callback
                 * @param errorCallback error callback
                 */
                sendResetPasswordRequest: function (form, successCallback, errorCallback) {
                    FormService.send("POST", "/reset/", form, successCallback, errorCallback);
                },

                /**
                 * Sends password reset request.
                 * @param form form
                 * @param url post url
                 * @param successCallback success callback
                 * @param errorCallback error callback
                 */
                resetPassword: function (form, url, successCallback, errorCallback) {
                    FormService.send("POST", url, form, successCallback, errorCallback);
                },

                /**
                 * Register new account
                 * @param account new account
                 * @returns user promise object.
                 */
                register: function (account) {
                    return Registration.register(account);
                },

                /**
                 * Check if app user is logged in.
                 * @returns true if user is logged in
                 */
                isLoggedIn: function () {
                    return !!this.getCookie("user_token");
                },

                /**
                 * Retrieves cookie value by provided cookie name.
                 * @param cname cookie name
                 */
                getCookie: function getCookie(cname) {
                    var name = cname + "=";
                    var ca = document.cookie.split(';');
                    for (var i = 0; i < ca.length; i++) {
                        var c = ca[i];
                        while (c.charAt(0) == ' ') c = c.substring(1);
                        if (c.indexOf(name) != -1) return c.substring(name.length, c.length);
                    }
                    return "";
                }
            };
        }]);

        /**
         * List lazy loading service (used fot lazy load lists of messages, bookings and items in dashboard).
         */
        EloueCommon.factory("LazyLoader", ["$timeout", "$rootScope", "$q", function ($timeout, $rootScope, $q) {
            var config,
                data,
                fetch,
                args;
            return {

                configure: function (options) {
                    config = options;
                    data = config.data;
                    fetch = config.fetchData;
                    args = config.args;
                },

                getData: function () {
                    var deferred = $q.defer();
                    $rootScope.$broadcast("showLoading");

                    fetch.apply(null, args).then(function (res) {
                        deferred.resolve(res);
                        $rootScope.$broadcast("hideLoading");
                    });

                    return deferred.promise;
                },

                load: function () {
                    var deferred = $q.defer();
                    var _this = this;

                    $rootScope.$broadcast("showLoading");

                    _this.getData().then(function (col) {
                        deferred.resolve(col);
                    });

                    return deferred.promise;
                }
            }
        }]);

        /**
         * Service to store server side validation errors.
         */
        EloueCommon.factory("ServerValidationService", function () {
            var formErrors={}, rootErrors="rootErrors";

            return {
                addErrors: function(messageError, description, fieldErrors, formTag) {
                    if(!formTag){
                        formTag = rootErrors;
                    }
                    formErrors[formTag] = {
                        message: messageError,
                        fields: fieldErrors
                    };
                    if(!!description){
                        formErrors[formTag].description=(""+description).replace("[","").replace("]","").replace("{","").replace("}","");
                    }
                },
                removeErrors: function(formTag){
                    if(!formTag){
                        formTag = rootErrors;
                    }
                    delete formErrors[formTag];
                },
                getFormErrorMessage: function(formTag){
                    if(!formTag){
                        formTag = rootErrors;
                    }
                    if((!formErrors[formTag] || (!formErrors[formTag].message && !formErrors[formTag].description))) {
                        return undefined;
                    }
                    return { message: formErrors[formTag].message, description: formErrors[formTag].description};
                },
                getFieldError: function(fieldName, formTag){
                    if(!formTag){
                        formTag = rootErrors;
                    }
                    if(!formErrors[formTag] || !formErrors[formTag].fields){
                        return undefined;
                    }
                    return formErrors[formTag].fields[fieldName];
                },
                getErrors: function(formTag){
                    if(!formTag){
                        formTag = rootErrors;
                    }
                    return formErrors[formTag];
                },
                addError: function(field, message, formTag){
                    if(!formTag){
                        formTag = rootErrors;
                    }
                    if(!formErrors[formTag]){
                        formErrors[formTag] = {};
                    }
                    if(!formErrors[formTag].fields){
                        formErrors[formTag].fields = {};
                    }
                    formErrors[formTag].fields[field] = message;
                }
            }
        });


        EloueCommon.factory("ToDashboardRedirectService", ["$window", "$cookies", function ($window, $cookies) {

            return {
                showPopupAndRedirect: function (href) {
                    var delay,
                        modalView = $('#redirect'),
                        eloueRedirectUrl = $('#eloue_url_redirect'),
                        redirectResult;
                    if (!modalView || modalView.length == 0) {
                        delay = 0;
                    } else {
                        delay = 5000;
                        modalView.modal('show');
                    }
                    if(!eloueRedirectUrl || eloueRedirectUrl.length == 0){
                        redirectResult=href;
                    } else {
                        redirectResult=eloueRedirectUrl.val()+"?url="+encodeURIComponent(href)+"&user_token="+$cookies.user_token;
                    }

                    setTimeout(function () {
                        $window.location.href = redirectResult;
                    }, delay);
                }
            }
        }]);
    });