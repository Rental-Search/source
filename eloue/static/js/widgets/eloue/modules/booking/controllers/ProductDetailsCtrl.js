define(["angular", "toastr", "eloue/modules/booking/BookingModule",
    "../../../../../common/eloue/values",
    "../../../../../common/eloue/services"
], function (angular, toastr) {
    "use strict";

    angular.module("EloueApp.BookingModule").controller("ProductDetailsCtrl", [
        "$scope",
        "$window",
        "$location",
        "Endpoints",
        "CivilityChoices",
        "ProductsLoadService",
        "MessageThreadsService",
        "ProductRelatedMessagesLoadService",
        "UsersService",
        "AuthService",
        "AddressesService",
        "CreditCardsService",
        "BookingsLoadService",
        "BookingsService",
        "PhoneNumbersService",
        "CategoriesService",
        "UtilsService",
        "ShippingsService",
        "ShippingPointsService",
        "ProductShippingPointsService",
        "PatronShippingPointsService",
        "ToDashboardRedirectService",
        function ($scope, $window, $location, Endpoints, CivilityChoices, ProductsLoadService, MessageThreadsService, ProductRelatedMessagesLoadService, UsersService, AuthService, AddressesService, CreditCardsService, BookingsLoadService, BookingsService, PhoneNumbersService, CategoriesService, UtilsService, ShippingsService, ShippingPointsService, ProductShippingPointsService, PatronShippingPointsService, ToDashboardRedirectService) {

            $scope.creditCard = {
                id: null,
                card_number: "",
                expires: "",
                holder: "",
                masked_number: "",
                cvv: "",
                keep: "",
                holder_name: "",
                subscriber_reference: ""
            };
            $scope.newCreditCard = true;
            $scope.addShipping = false;
            $scope.borrowerShippingPoints = [];
            $scope.submitInProgress = false;
            $scope.showSaveCard = true;
            $scope.selectedMonthAndYear = Date.today().getMonth() + " " + Date.today().getFullYear();
            $scope.showUnavailable = true;
            $scope.showBookings = true;
            $scope.bookings = [];
            $scope.currentBookings = [];
            $scope.weeks = {};
            var months = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"];

            $scope.monthOptions = [
                {name: months[Date.today().add(-1).months().getMonth()] + " " + Date.today().add(-1).months().getFullYear(), value: Date.today().add(-1).months().getMonth() + " " + Date.today().add(-1).months().getFullYear()},
                {name: months[Date.today().getMonth()] + " " + Date.today().getFullYear(), value: Date.today().getMonth() + " " + Date.today().getFullYear()},
                {name: months[Date.today().add(1).months().getMonth()] + " " + Date.today().add(1).months().getFullYear(), value: Date.today().add(1).months().getMonth() + " " + Date.today().add(1).months().getFullYear()},
                {name: months[Date.today().add(2).months().getMonth()] + " " + Date.today().add(2).months().getFullYear(), value: Date.today().add(2).months().getMonth() + " " + Date.today().add(2).months().getFullYear()},
                {name: months[Date.today().add(3).months().getMonth()] + " " + Date.today().add(3).months().getFullYear(), value: Date.today().add(3).months().getMonth() + " " + Date.today().add(3).months().getFullYear()},
                {name: months[Date.today().add(4).months().getMonth()] + " " + Date.today().add(4).months().getFullYear(), value: Date.today().add(4).months().getMonth() + " " + Date.today().add(4).months().getFullYear()},
                {name: months[Date.today().add(5).months().getMonth()] + " " + Date.today().add(5).months().getFullYear(), value: Date.today().add(5).months().getMonth() + " " + Date.today().add(5).months().getFullYear()},
                {name: months[Date.today().add(6).months().getMonth()] + " " + Date.today().add(6).months().getFullYear(), value: Date.today().add(6).months().getMonth() + " " + Date.today().add(6).months().getFullYear()},
                {name: months[Date.today().add(7).months().getMonth()] + " " + Date.today().add(7).months().getFullYear(), value: Date.today().add(7).months().getMonth() + " " + Date.today().add(7).months().getFullYear()},
                {name: months[Date.today().add(8).months().getMonth()] + " " + Date.today().add(8).months().getFullYear(), value: Date.today().add(8).months().getMonth() + " " + Date.today().add(8).months().getFullYear()},
                {name: months[Date.today().add(9).months().getMonth()] + " " + Date.today().add(9).months().getFullYear(), value: Date.today().add(9).months().getMonth() + " " + Date.today().add(9).months().getFullYear()},
                {name: months[Date.today().add(10).months().getMonth()] + " " + Date.today().add(10).months().getFullYear(), value: Date.today().add(10).months().getMonth() + " " + Date.today().add(10).months().getFullYear()},
                {name: months[Date.today().add(11).months().getMonth()] + " " + Date.today().add(11).months().getFullYear(), value: Date.today().add(11).months().getMonth() + " " + Date.today().add(11).months().getFullYear()},
                {name: months[Date.today().add(12).months().getMonth()] + " " + Date.today().add(12).months().getFullYear(), value: Date.today().add(12).months().getMonth() + " " + Date.today().add(12).months().getFullYear()}
            ];

            // Read authorization token
            $scope.currentUserToken = AuthService.getCookie("user_token");

            if (!!$scope.currentUserToken) {
                // Get current user
                $scope.currentUserPromise = UsersService.getMe().$promise;
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    if (!currentUser.default_address) {
                        $scope.noAddress = true;
                    }
                    $scope.loadCreditCards();
                });
            }

            /**
             * Retrieve product ID from url. Url usually is like /location/{{root_category_slug}}/{{node_category_slug}}/{{leaf_category_slug}}/{{product_slug}}-{{product_id}}
             * @returns {string|*}
             */
            $scope.getProductIdFromUrl = function () {
                var href = $window.location.href;
                href = href.substr(href.lastIndexOf("location/") + 8);

                $scope.rootCategory = href.split("/")[1];
                var subparts = href.split("-");
                var productId = subparts[subparts.length - 1];
                var lastIndex = productId.indexOf("/") > 0 ? productId.indexOf("/") : (productId.length - 1);
                return productId.substr(0, lastIndex);
            };
            $scope.productId = $scope.getProductIdFromUrl();

            /**
             * Initial booking dates are 1 nad 2 days after todat, 8a.m.
             */
            $scope.bookingDetails = {
                "fromDate": Date.today().add(1).days().toString("dd/MM/yyyy"),
                "fromHour": "08:00:00",
                "toDate": Date.today().add(2).days().toString("dd/MM/yyyy"),
                "toHour": "08:00:00"
            };
            var fromDateSelector = $("input[name='fromDate']"), toDateSelector = $("input[name='toDate']");
            fromDateSelector.val(Date.today().add(1).days().toString("dd/MM/yyyy")).datepicker({
                language: "fr",
                autoclose: true,
                startDate: Date.today().add(1).days().toString("dd/MM/yyyy")
            });
            toDateSelector.val(Date.today().add(2).days().toString("dd/MM/yyyy")).datepicker({
                language: "fr",
                autoclose: true,
                startDate: Date.today().add(2).days().toString("dd/MM/yyyy")
            });
            $scope.duration = "0 jour";
            $scope.bookingPrice = 0;
            $scope.shippingPrice = 0;
            //not show zero price before request ended
            //$scope.pricePerDay = 0;
            $scope.caution = 0;
            $scope.productRelatedMessages = [];
            $scope.ownerCallDetails = {};
            $scope.ownerCallDetailsError = null;
            $scope.available = true;
            $scope.newMessage = {};
            $scope.threadId = null;
            $scope.civilityOptions = CivilityChoices;
            $scope.hours = [
                {"label": "00h", "value": "00:00:00"},
                {"label": "01h", "value": "01:00:00"},
                {"label": "02h", "value": "02:00:00"},
                {"label": "03h", "value": "03:00:00"},
                {"label": "04h", "value": "04:00:00"},
                {"label": "05h", "value": "05:00:00"},
                {"label": "06h", "value": "06:00:00"},
                {"label": "07h", "value": "07:00:00"},
                {"label": "08h", "value": "08:00:00"},
                {"label": "09h", "value": "09:00:00"},
                {"label": "10h", "value": "10:00:00"},
                {"label": "11h", "value": "11:00:00"},
                {"label": "12h", "value": "12:00:00"},
                {"label": "13h", "value": "13:00:00"},
                {"label": "14h", "value": "14:00:00"},
                {"label": "15h", "value": "15:00:00"},
                {"label": "16h", "value": "16:00:00"},
                {"label": "17h", "value": "17:00:00"},
                {"label": "18h", "value": "18:00:00"},
                {"label": "19h", "value": "19:00:00"},
                {"label": "20h", "value": "20:00:00"},
                {"label": "21h", "value": "21:00:00"},
                {"label": "22h", "value": "22:00:00"},
                {"label": "23h", "value": "23:00:00"}
            ];

            /**
             * Show response errors on booking form under appropriate field.
             * @param error JSON object with error details
             */
            $scope.handleResponseErrors = function(error) {
                // Hide all spinners and enable form controls.
                $scope.submitInProgress = false;
                $scope.loadingProductShippingPoint = false;
                $scope.shippingPointsRequestInProgress = false;
            };

            ProductsLoadService.getProduct($scope.productId, false, false).then(function (result) {
                $scope.product = result;
                //TODO: uncomment, when calendar tab is displayed on product details page
//                $scope.loadCalendar();
            });

            /**
             * Update the product booking price based on selected duration.
             */
            $scope.updatePrice = function updatePrice() {
                var fromDateTimeStr = $scope.bookingDetails.fromDate + " " + $scope.bookingDetails.fromHour;
                var toDateTimeStr = $scope.bookingDetails.toDate + " " + $scope.bookingDetails.toHour;
                var fromDateTime = Date.parseExact(fromDateTimeStr, "dd/MM/yyyy HH:mm:ss");
                var toDateTime = Date.parseExact(toDateTimeStr, "dd/MM/yyyy HH:mm:ss");
                toDateSelector.datepicker("setStartDate", fromDateTime);
                toDateSelector.datepicker("update");
                var today = Date.today().set({hour: 8, minute: 0});
                $scope.dateRangeError = "";
                if (fromDateTime > toDateTime) {
                    //When the user change the value of the "from date" and that this new date is after the "to date" so the "to date" should be update and the value should be the same of the "from date".
                    $scope.dateRangeError = "La date de début ne peut pas être après la date de fin";
                    if (fromDateTime.getHours() < 23) {
                        $scope.bookingDetails.toDate = fromDateTime.toString("dd/MM/yyyy");
                        $scope.bookingDetails.toHour = fromDateTime.add(1).hours().toString("HH:mm:ss");
                    } else {
                        $scope.bookingDetails.toDate = fromDateTime.add(1).days().toString("dd/MM/yyyy");
                        $scope.bookingDetails.toHour = fromDateTime.add(1).hours().toString("HH:mm:ss");
                    }
                    fromDateTimeStr = $scope.bookingDetails.fromDate + " " + $scope.bookingDetails.fromHour;
                    toDateTimeStr = $scope.bookingDetails.toDate + " " + $scope.bookingDetails.toHour;
                }
                $scope.dateRangeError = null;
                // check if product is available for selected dates
                ProductsLoadService.isAvailable($scope.productId, fromDateTimeStr, toDateTimeStr, "1").then(function (result) {
                    var price = result.total_price;
                    price = price.replace("€","").replace("\u20ac","").replace("Eu","").replace(",",".").replace(" ","");
                    price = Number(price);
                    $scope.duration = result.duration;
                    $scope.pricePerDay = result.unit_value;
                    $scope.bookingPrice = price;
                    $scope.available = result.max_available > 0;
                }, function (error) {
                    $scope.available = false;
                    $scope.handleResponseErrors(error);
                });
            };

            /**
             * Send new message to the owner.
             */
            $scope.sendMessage = function sendMessage() {
                ProductRelatedMessagesLoadService.postMessage($scope.threadId, $scope.currentUser.id, $scope.product.owner.id,
                    $scope.newMessage.body, null, $scope.product.id).then(function (result) {
                        $scope.loadAdWordsTags("SfnGCMvgrgMQjaaF6gM");
                        $scope.trackEvent("Réservation", "Message",  $scope.getEventLabel());
                        $scope.trackPageView();
                        // Clear message field
                        $scope.newMessage = {};
                        $scope.productRelatedMessages.push(result);
                        $scope.loadMessageThread();
                    });
            };

            /**
             * Handler for call owner button.
             */
            $scope.callOwner = function callOwner() {
                //TODO: call real service
                console.log("Calling product owner..");
            };

            $scope.selectedPointId = "";

            $scope.pointSelected = function(pointId) {
                $scope.selectedPointId = pointId;
                $scope.shippingPrice = 10;
            };

            $scope.saveDefaultAddress = function() {
                $scope.submitInProgress = true;
                $scope.currentUser.default_address.country = "FR";
                AddressesService.saveAddress($scope.currentUser.default_address).$promise.then(function (result) {
                    $scope.submitInProgress = false;
                    $scope.currentUser.default_address = result;
                    UsersService.updateUser({default_address: Endpoints.api_url + "addresses/" + result.id + "/"});
                    $scope.noAddress = false;
                    $scope.loadShippingPoints();
                }, function (error) {
                    $scope.handleResponseErrors(error);
                });
            };

            $scope.sendBookingRequest = function () {
                //if user has no default addrees, firstly save his address
                if ($scope.noAddress) {
                    $scope.submitInProgress = true;
                    $scope.currentUser.default_address.country = "FR";
                    AddressesService.saveAddress($scope.currentUser.default_address).$promise.then(function (result) {
                        $scope.currentUser.default_address = result;
                        UsersService.updateUser({default_address: Endpoints.api_url + "addresses/" + result.id + "/"});
                        $scope.saveCardAndRequestBooking();
                    }, function (error) {
                        $scope.handleResponseErrors(error);
                    });
                } else {
                    $scope.saveCardAndRequestBooking();
                }

            };

            /**
             * Save payment info and request product booking.
             */
            $scope.saveCardAndRequestBooking = function() {
                $scope.submitInProgress = true;
                // Update user info
                //TODO: patch more fields
                var userPatch = {};
                userPatch.first_name = $scope.currentUser.first_name;
                userPatch.last_name = $scope.currentUser.last_name;
                if ($scope.isAuto()) {
                    userPatch.drivers_license_number = $scope.currentUser.drivers_license_number;
                    if ($scope.currentUser.drivers_license_date) {
                        userPatch.drivers_license_date =UtilsService.formatDate($scope.currentUser.drivers_license_date, "yyyy-MM-dd'T'HH:mm");
                    }
                    userPatch.place_of_birth = $scope.currentUser.place_of_birth;
                    if ($scope.currentUser.date_of_birth) {
                        userPatch.date_of_birth =UtilsService.formatDate($scope.currentUser.date_of_birth, "yyyy-MM-dd'T'HH:mm");
                    }
                }

                UsersService.updateUser(userPatch).$promise.then(function (result) {
                    // Update credit card info
                    $scope.creditCard.expires = $scope.creditCard.expires.replace("/", "");
                    // If credit card exists now it is deleted and saved again
                    if ($scope.creditCard.masked_number == "") {
                        if (!!$scope.creditCard.id) {
                            CreditCardsService.deleteCard($scope.creditCard).$promise.then(function (result) {
                                CreditCardsService.saveCard($scope.creditCard).$promise.then(function (result) {
                                    $scope.requestBooking();
                                }, function (error) {
                                    $scope.handleResponseErrors(error);
                                });
                            });
                        } else {
                            CreditCardsService.saveCard($scope.creditCard).$promise.then(function (result) {
                                $scope.requestBooking();
                            }, function (error) {
                                $scope.handleResponseErrors(error);
                            });
                        }
                    } else {
                        $scope.requestBooking();
                    }
                }, function (error) {
                    $scope.handleResponseErrors(error);
                });
            };

            /**
             * Save booking and make payment request.
             */
            $scope.requestBooking = function () {
                var booking = {};
                var fromDateTimeStr = $scope.bookingDetails.fromDate + " " + $scope.bookingDetails.fromHour;
                var toDateTimeStr = $scope.bookingDetails.toDate + " " + $scope.bookingDetails.toHour;
                var fromDateTime = Date.parseExact(fromDateTimeStr, "dd/MM/yyyy HH:mm:ss");
                var toDateTime = Date.parseExact(toDateTimeStr, "dd/MM/yyyy HH:mm:ss");
                booking.started_at = fromDateTime.toString("yyyy-MM-ddTHH:mm");
                booking.ended_at = toDateTime.toString("yyyy-MM-ddTHH:mm");
                booking.owner = Endpoints.api_url + "users/" + $scope.product.owner.id + "/";
                booking.borrower = Endpoints.api_url + "users/" + $scope.currentUser.id + "/";
                booking.product = Endpoints.api_url + "products/" + $scope.product.id + "/";
                // Create booking
                BookingsLoadService.requestBooking(booking).then(
                    function (booking) {
                        var paymentInfo = {};
                        if ($scope.creditCard.card_number && $scope.creditCard.cvv) {
                            paymentInfo = {
                                card_number: $scope.creditCard.card_number,
                                expires: $scope.creditCard.expires,
                                cvv: $scope.creditCard.cvv,
                                holder_name: $scope.creditCard.holder_name
                            };
                        } else {
                            // send only credit card link if using saved credit card
                            paymentInfo = {
                                credit_card: Endpoints.api_url + "credit_cards/" + $scope.creditCard.id + "/"
                            };
                        }

                        //TODO: save user shipping point and product shipping
                        console.log($scope.borrowerShippingPoints);
                        var selectedPoint = {};
                        angular.forEach($scope.borrowerShippingPoints, function (value, key) {
                            if($scope.selectedPointId == value.site_id) {
                                selectedPoint = value;
                            }
                        });
                        if (!!selectedPoint && !!selectedPoint.site_id) {
                            selectedPoint.type = 2;
                            selectedPoint.booking = Endpoints.api_url + "bookings/" + booking.uuid + "/";
                            selectedPoint.patron = Endpoints.api_url + "users/" + $scope.currentUser.id + "/";
                            PatronShippingPointsService.saveShippingPoint(selectedPoint).$promise.then(function (shippingPoint) {
                                $scope.payForBooking(booking, paymentInfo);
                            }, function (error) {
                                $scope.handleResponseErrors(error);
                            });
                        } else {
                            $scope.payForBooking(booking, paymentInfo);
                        }
                    }, function (error) {
                        $scope.handleResponseErrors(error);
                    }
                );
            };

            $scope.payForBooking = function (booking, paymentInfo) {
                BookingsLoadService.payForBooking(booking.uuid, paymentInfo).then(function (result) {
                    $scope.loadAdWordsTags("-XHsCMvspQMQjaaF6gM");
                    $scope.trackEvent("Réservation", "Demande de réservation",  $scope.getEventLabel());
                    $scope.trackPageView();
                    toastr.options.positionClass = "toast-top-full-width";
                    toastr.success("Réservation enregistré", "-XHsCMvspQMQjaaF6gM");
                    $(".modal").modal("hide");
                    //$window.location.href = "/dashboard/#/bookings/" + booking.uuid;
                    $scope.submitInProgress = false;
                    ToDashboardRedirectService.showPopupAndRedirect("/dashboard/#/bookings/" + booking.uuid);
                }, function (error) {
                    $scope.handleResponseErrors(error);
                });
            };

            /**
             * Get label for google analytics event base on product category.
             * @returns event tag label
             */
            $scope.getEventLabel = function() {
                if ($scope.isAuto()) {
                    return "Voiture - " + $scope.productCategoryName;
                } else if ($scope.isRealEstate()) {
                    return "Logement - " + $scope.productCategoryName;
                } else {
                    return "Objet - " + $scope.productCategoryAncestors;
                }
            };

            /**
             * Clears credit card data, when user clicks link to modify payment info.
             */
            $scope.clearCreditCard = function () {
                $scope.newCreditCard = true;
                $scope.creditCard = {
                    id: $scope.creditCard.id,
                    card_number: "",
                    expires: "",
                    holder: "",
                    masked_number: "",
                    cvv: "",
                    keep: "",
                    holder_name: "",
                    subscriber_reference: ""
                };
            };

            $scope.updatePrice();

            /**
             * Catch "redirectToLogin" event
             */
            $scope.$on("redirectToLogin", function () {
                $location.path("/login");
            });

            /**
             * Load necessary data on modal window open event based on modal name.
             */
            $scope.$on("openModal", function (event, args) {
                if ((args.name === "message") && $scope.productRelatedMessages.length == 0) {
                    $scope.loadMessageThread();
                } else if (args.name === "booking") {
                    $scope.loadCreditCards();
                    $scope.loadProductShippingPoint();
                } else if (args.name === "phone") {
                    $scope.loadPhoneDetails();
                }
                if (args.name != "login") {
                    if ($scope.currentUser && !$scope.currentUser.default_address) {
                        $scope.noAddress = true;
                    }
                    if (!$scope.product) {
                        ProductsLoadService.getProduct($scope.productId, false, false).then(function (result) {
                            $scope.product = result;
                            $scope.loadPictures();
                            $scope.loadProductCategoryAncestors(args.name);
                        });
                    } else {
                        $scope.loadPictures();
                        $scope.loadProductCategoryAncestors(args.name);
                    }
                }
            });

            /**
             * Loads all ancestors of product category for analytics tags.
             * @param modalName name of modal window
             */
            $scope.loadProductCategoryAncestors = function (modalName) {
                $scope.productCategoryName = $scope.product.category.name;
                CategoriesService.getAncestors($scope.product.category.id).then(function (ancestors) {
                    var categoriesStr = "";
                    angular.forEach(ancestors, function (value, key) {
                        categoriesStr = categoriesStr + value.name + " - ";
                    });
                    $scope.productCategoryAncestors = categoriesStr + $scope.product.category.name;
                    if (modalName === "phone") {
                        $scope.trackEvent("Réservation", "Appel", $scope.getEventLabel());
                        $scope.trackPageView();
                    }
                });
            };

            $scope.loadPictures = function () {
                var picturesDataArray = $scope.product.pictures;
                // Parse pictures
                if (angular.isArray(picturesDataArray) && picturesDataArray.length > 0) {
                    $scope.product.picture = picturesDataArray[0].image.thumbnail;
                }
            };

            /**
             * Restore path when closing modal window.
             */
            $scope.$on("closeModal", function (event, args) {
                var currentPath = $location.path();
                var newPath = currentPath.slice(0, currentPath.indexOf(args.name));
                $location.path(newPath);
                $scope.$apply();
            });

            /**
             * Load premium phone number using product's phone number id.
             */
            $scope.loadPhoneDetails = function () {
                var phoneId = null;
                if ($scope.product) {
                    // Try to get owner default number first. Use product phone otherwise.
                    if ($scope.product.owner.default_number && $scope.product.owner.default_number.id) {
                        phoneId = $scope.product.owner.default_number.id;
                    } else if ($scope.product.phone && $scope.product.phone.id) {
                        phoneId = $scope.product.phone.id
                    }
                }
                if (phoneId) {
                    PhoneNumbersService.getPremiumRateNumber(phoneId).$promise.then(function (result) {
                        if (!result.error || result.error == "0") {
                            $scope.ownerCallDetails = {
                                number: result.numero,
                                tariff: result.tarif
                            };
                        } else {
                            $scope.ownerCallDetailsError = !!result.error_msg ? result.error_msg : "Le numero n'est pas disponible";
                        }
                    });
                } else {
                    $scope.ownerCallDetailsError = "Le numero n'est pas disponible";
                }
            };

            /**
             * Parses user creadit card info.
             */
            $scope.loadCreditCards = function () {
                if (!$scope.currentUserPromise) {
                    $scope.currentUserPromise = UsersService.getMe().$promise;
                }
                $scope.currentUserPromise.then(function (currentUser) {
                    $scope.currentUser = currentUser;
                    if (!currentUser.default_address) {
                        $scope.noAddress = true;
                    }
                    if (!!$scope.currentUser.creditcard) {
                        var card = $scope.currentUser.creditcard;
                        $scope.creditCard = card;
                        $scope.creditCard.expires = card.expires.slice(0, 2) + "/" + card.expires.slice(2);
                        $scope.newCreditCard = false;
                    }
                });
            };

            $scope.loadProductShippingPoint = function () {
                $scope.currentUserPromise.then(function (currentUser) {
                    $scope.currentUser = currentUser;
                    $scope.loadingProductShippingPoint = true;
                    ProductShippingPointsService.getByProduct($scope.productId).then(function (data) {
                        //Show shipping choice only if there are existing product shipping points
                        if (!!data.results && data.results.length > 0) {
                            $scope.productShippingPoint = data.results[0];
                            $scope.shippingAllowed = true;
                        }
                        $scope.loadingProductShippingPoint = false;
                    }, function (error) {
                        $scope.handleResponseErrors(error);
                    });
                });
            };

            $scope.loadShippingPoints = function () {
                if ($scope.addShipping && $scope.borrowerShippingPoints.length == 0) {
                    if (!!$scope.currentUser.default_address) {
                        $scope.shippingPointsRequestInProgress = true;
                        var shippingPointsPromise = {};
                        if (!$scope.currentUser.default_address.position) {
                            var addressString = $scope.currentUser.default_address.zipcode + " " + $scope.currentUser.default_address.street + " " + $scope.currentUser.default_address.city;
                            shippingPointsPromise = ShippingPointsService.searchArrivalShippingPointsByAddressAndProduct(addressString, $scope.productId);
                        } else {
                            shippingPointsPromise = ShippingPointsService.searchArrivalShippingPointsByCoordinatesAndProduct($scope.currentUser.default_address.position.coordinates[0], $scope.currentUser.default_address.position.coordinates[1], $scope.productId);
                        }
                        shippingPointsPromise.then(function (result) {
                            $scope.shippingPointsRequestInProgress = false;
                            //TODO: it's temperory, then will call pricing service
                            angular.forEach(result, function (value, key) {
                                value.price = "10.0";
                            });
                            $scope.borrowerShippingPoints = result;
                            $("#point-contatiner").mCustomScrollbar({
                                scrollInertia: '100',
                                autoHideScrollbar: false,
                                theme: 'dark-thin',
                                advanced: {
                                    updateOnContentResize: true,
                                    autoScrollOnFocus: false
                                }
                            });
                        }, function (error) {
                            $scope.handleResponseErrors(error);
                        });
                    }
                }
                if (!$scope.addShipping) {
                    $scope.shippingPrice = 0;
                    $scope.selectedPointId = "";
                }
            };

            $scope.isAuto = function () {
                return ($scope.rootCategory === "automobile");
            };

            $scope.isRealEstate = function () {
                return ($scope.rootCategory === "location-saisonniere");
            };

            /**
             * Loads message thread for send message to owner modal window.
             */
            $scope.loadMessageThread = function () {
                if (!$scope.currentUserPromise) {
                    $scope.currentUserPromise = UsersService.getMe().$promise;
                }
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    MessageThreadsService.getMessageThread($scope.productId, $scope.currentUser.id).then(function (result) {
                        angular.forEach(result, function (value, key) {
                            $scope.threadId = UtilsService.getIdFromUrl(value.thread);
                        });
                        $scope.productRelatedMessages = result;
                    });
                });
            };

            /**
             * Used to load calendar with prodcut booking data.
             */
            $scope.loadCalendar = function () {
                BookingsService.getBookingsByProduct($scope.product.id).then(function (bookings) {

                    angular.forEach(bookings, function (value, key) {
                        value.startDay = Date.parse(value.start_date.day + " " + value.start_date.month + " " + value.start_date.year);
                        value.endDay = Date.parse(value.end_date.day + " " + value.end_date.month + " " + value.end_date.year);
                    });
                    $scope.bookings = bookings;

                    $scope.updateCalendar();
                });
            };

            $scope.updateCalendar = function () {
                $scope.currentBookings = [];
                var s = $scope.selectedMonthAndYear.split(" ");
                var date = new Date();
                date.setMonth(s[0]);
                date.setFullYear(s[1]);
                var weeks = [];
                var start = new Date(date.moveToFirstDayOfMonth());
                for (var i = 0; i < 6; i++) {
                    var currentDay = start.moveToDayOfWeek(1, -1);
                    var days = [];
                    for (var j = 0; j < 7; j++) {
                        var isBooked = false;
                        angular.forEach($scope.bookings, function (value, key) {
                            if (currentDay.between(value.startDay, value.endDay)) {
                                isBooked = true;
                                $scope.currentBookings.push(value);
                            }
                        });

                        days.push({dayOfMonth: currentDay.getDate(), isBooked: isBooked});
                        currentDay.add(1).days();
                    }

                    var week = {};
                    week.weekDays = days;
                    weeks.push(week);
                    start.add(1).weeks();
                }
                $scope.weeks = weeks;
            };

            $scope.onShowUnavailable = function () {
                //TODO: implement when product availability is added to the model
            };

            $scope.onShowBookings = function () {
                console.log("onShowBookings");
            };

            /**
             * Select tab in main product detail page content part.
             */
            $scope.selectTab = function (tabName) {
                $('[id^=tabs-]').each(function () {
                    var item = $(this);
                    if (("#" + item.attr("id")) == tabName) {
                        item.removeClass("ng-hide");
                    } else {
                        item.addClass("ng-hide");
                    }
                });
                $('a[href^=#tabs-]').each(function () {
                    var item = $(this);
                    if (item.attr("href") == tabName) {
                        item.addClass("current");
                    } else {
                        item.removeClass("current");
                    }
                });
            };

            $scope.selectTab("#tabs-photos");

            /**
             * Add Google ad scripts.
             */
            $scope.loadAdWordsTags =  function(googleConversionLabel) {
                $window.google_trackConversion({
                    google_conversion_id: 1027691277,
                    google_conversion_language: "en",
                    google_conversion_format: "3",
                    google_conversion_color: "ffffff",
                    google_conversion_label: googleConversionLabel,
                    google_conversion_value: 1.00,
                    google_conversion_currency: "EUR",
                    google_remarketing_only: false
                });
            };

            $("#date_of_birth").datepicker({
                language: "fr",
                autoclose: true,
                todayHighlight: true,
                dateFormat: "yyyy-MM-dd"
            });

            $("#drivers_license_date").datepicker({
                language: "fr",
                autoclose: true,
                todayHighlight: true,
                dateFormat: "yyyy-MM-dd"
            });

            /**
             * Push track event to Google Analytics.
             *
             * @param category category
             * @param action action
             * @param value value
             */
            $scope.trackEvent = function(category, action, value) {
                _gaq.push(["_trackEvent", category, action, value]);
            };

            /**
             * Push track page view to Google Analytics.
             */
            $scope.trackPageView = function() {
                _gaq.push(["_trackPageview", $window.location.href + "/success/"]);
            };
        }]);
});
