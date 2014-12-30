define([
    "eloue/app",
    "../../../../../bower_components/toastr/toastr",
    "../../../../common/eloue/values",
    "../../../../common/eloue/services/ProductsService",
    "../../../../common/eloue/services/MessageThreadsService",
    "../../../../common/eloue/services/ProductRelatedMessagesService",
    "../../../../common/eloue/services/UsersService",
    "../../../../common/eloue/services/AuthService",
    "../../../../common/eloue/services/AddressesService",
    "../../../../common/eloue/services/CreditCardsService",
    "../../../../common/eloue/services/BookingsService",
    "../../../../common/eloue/services/PhoneNumbersService",
    "../../../../common/eloue/services/CategoriesService",
    "../../../../common/eloue/services/UtilsService",
    "../../../../common/eloue/services/ShippingPointsService",
    "../../../../common/eloue/services/ProductShippingPointsService",
    "../../../../common/eloue/services/PatronShippingPointsService",
    "../../../../common/eloue/services/ToDashboardRedirectService",
    "../../../../common/eloue/services/ScriptTagService"
], function (EloueWidgetsApp, toastr) {
    "use strict";
    /**
     * Controller for widgets on product details page that are related to booking.
     */
    EloueWidgetsApp.controller("BookingCtrl", [
        "$scope",
        "$window",
        "$location",
        "$timeout",
        "Endpoints",
        "CivilityChoices",
        "ProductsService",
        "MessageThreadsService",
        "ProductRelatedMessagesService",
        "UsersService",
        "AuthService",
        "AddressesService",
        "CreditCardsService",
        "BookingsService",
        "PhoneNumbersService",
        "CategoriesService",
        "UtilsService",
        "ShippingPointsService",
        "ProductShippingPointsService",
        "PatronShippingPointsService",
        "ToDashboardRedirectService",
        "ScriptTagService",
        function ($scope, $window, $location, $timeout, Endpoints, CivilityChoices, ProductsService, MessageThreadsService, ProductRelatedMessagesService, UsersService, AuthService, AddressesService, CreditCardsService, BookingsService, PhoneNumbersService, CategoriesService, UtilsService, ShippingPointsService, ProductShippingPointsService, PatronShippingPointsService, ToDashboardRedirectService, ScriptTagService) {

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
            $scope.bookings = [];
            $scope.currentBookings = [];
            $scope.isAuto = false;
            $scope.isRealEstate = false;

            // Read authorization token
            $scope.currentUserToken = AuthService.getUserToken();

            if ($scope.currentUserToken) {
                // Get current user
                $scope.currentUserPromise = UsersService.getMe();
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
                // "cut" URL to last hash index or to last slash index
                var lastIndex = href.indexOf("#") > 0 ? href.lastIndexOf("#") - 1 : (href.length - 1);
                href = href.substr(0, lastIndex);
                $scope.rootCategory = href.split("/")[1];
                $scope.isAuto = ($scope.rootCategory === "automobile");
                $scope.isRealEstate = ($scope.rootCategory === "location-saisonniere");
                var subparts = href.split("-");
                return subparts[subparts.length - 1];
            };
            $scope.productId = $scope.getProductIdFromUrl();

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
             * Initial booking dates are 1 nad 2 days after todat, 8a.m.
             */
            $scope.bookingDetails = {
                "fromDate": Date.today().add(1).days().toString("dd/MM/yyyy"),
                "fromHour": $scope.hours[8],
                "toDate": Date.today().add(2).days().toString("dd/MM/yyyy"),
                "toHour": $scope.hours[9]
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

            /**
             * Show response errors on booking form under appropriate field.
             * @param error JSON object with error details
             */
            $scope.handleResponseErrors = function (error) {
                // Hide all spinners and enable form controls.
                $scope.submitInProgress = false;
                $scope.loadingProductShippingPoint = false;
                $scope.shippingPointsRequestInProgress = false;
            };

            ProductsService.getProduct($scope.productId, false, false).then(function (result) {
                $scope.product = result;
            });

            /**
             * Update the product booking price based on selected duration.
             */
            $scope.updatePrice = function updatePrice() {
                var fromDateTimeStr = $scope.bookingDetails.fromDate + " " + $scope.bookingDetails.fromHour.value,
                    toDateTimeStr = $scope.bookingDetails.toDate + " " + $scope.bookingDetails.toHour.value,
                    fromDateTime = Date.parseExact(fromDateTimeStr, "dd/MM/yyyy HH:mm:ss"),
                    toDateTime = Date.parseExact(toDateTimeStr, "dd/MM/yyyy HH:mm:ss");
                toDateSelector.datepicker("setStartDate", fromDateTime);
                toDateSelector.datepicker("update");
                $scope.dateRangeError = "";
                if (fromDateTime > toDateTime) {
                    //When the user change the value of the "from date" and that this new date is after the "to date" so the "to date" should be update and the value should be the same of the "from date".
                    $scope.dateRangeError = "La date de début ne peut pas être après la date de fin";
                    if (fromDateTime.getHours() < 23) {
                        $scope.bookingDetails.toDate = fromDateTime.toString("dd/MM/yyyy");
                        $scope.bookingDetails.toHour = $scope.findHour(fromDateTime.add(1).hours().toString("HH:mm:ss"));
                    } else {
                        $scope.bookingDetails.toDate = fromDateTime.add(1).days().toString("dd/MM/yyyy");
                        $scope.bookingDetails.toHour = $scope.findHour(fromDateTime.add(1).hours().toString("HH:mm:ss"));
                    }

                    // Fix for very strange eloueChosen directive behaviour. Sometimes directive doesn't get fired and
                    // UI doesn't change, but scope value was changed successfully.
                    $timeout(function () {
                        $("#toHour").trigger("chosen:updated");
                    }, 0);

                    fromDateTimeStr = $scope.bookingDetails.fromDate + " " + $scope.bookingDetails.fromHour;
                    toDateTimeStr = $scope.bookingDetails.toDate + " " + $scope.bookingDetails.toHour;
                }
                $scope.dateRangeError = null;
                // check if product is available for selected dates
                ProductsService.isAvailable($scope.productId, fromDateTimeStr, toDateTimeStr, "1").then(
                    $scope.parseProductAvailabilityResponse,
                    function (error) {
                        $scope.available = false;
                        $scope.handleResponseErrors(error);
                    }
                );
            };

            $scope.findHour = function(hourValue) {
                for (var i = 0; i < $scope.hours.length; i++) {
                    if ($scope.hours[i].value === hourValue) {
                        return $scope.hours[i];
                    }
                }
            };

            /**
             * Parse availability result.
             * @param result product availability check result
             */
            $scope.parseProductAvailabilityResponse = function (result) {
                var price = result.total_price;
                price = price.replace("€", "").replace("\u20ac", "").replace("Eu", "").replace(",", ".").replace(" ", "");
                price = Number(price);
                $scope.duration = result.duration;
                $scope.pricePerDay = result.unit_value;
                $scope.bookingPrice = price;
                $scope.available = result.max_available > 0;
            };

            /**
             * Send new message to the owner.
             */
            $scope.sendMessage = function sendMessage() {
                $scope.submitInProgress = true;
                ProductRelatedMessagesService.postMessage($scope.threadId, $scope.currentUser.id, $scope.product.owner.id,
                    $scope.newMessage.body, null, $scope.product.id).then(
                    $scope.updateThreadWithNewMessage,
                    function (error) {
                        $scope.available = false;
                        $scope.handleResponseErrors(error);
                    }
                );
            };

            /**
             * Call JS events and add new message to thread.
             * @param result newly created message
             */
            $scope.updateThreadWithNewMessage = function (result) {
                $scope.submitInProgress = false;
                ScriptTagService.loadAdWordsTags("SfnGCMvgrgMQjaaF6gM");
                ScriptTagService.trackEvent("Réservation", "Message", $scope.getEventLabel());
                ScriptTagService.trackPageView();
                // Clear message field
                $scope.newMessage = {};
                $scope.productRelatedMessages.push(result);
                $scope.loadMessageThread();
            };

            /**
             * Handler for call owner button.
             */
            $scope.callOwner = function () {};

            $scope.selectedPointId = "";

            $scope.pointSelected = function (pointId) {
                $scope.selectedPointId = pointId;
                $scope.shippingPrice = 10;
            };

            $scope.saveDefaultAddress = function () {
                $scope.submitInProgress = true;
                $scope.currentUser.default_address.country = "FR";
                AddressesService.saveAddress($scope.currentUser.default_address).then(
                    $scope.applyDefaultAddress,
                    $scope.handleResponseErrors
                );
            };

            $scope.applyDefaultAddress = function (result) {
                $scope.submitInProgress = false;
                $scope.currentUser.default_address = result;
                UsersService.updateUser({default_address: Endpoints.api_url + "addresses/" + result.id + "/"});
                $scope.noAddress = false;
                $scope.loadShippingPoints();
            };

            $scope.sendBookingRequest = function () {
                //if user has no default addrees, firstly save his address
                if ($scope.noAddress) {
                    $scope.submitInProgress = true;
                    $scope.currentUser.default_address.country = "FR";
                    AddressesService.saveAddress($scope.currentUser.default_address).then(
                        $scope.saveCardAndRequestBooking,
                        $scope.handleResponseErrors
                    );
                } else {
                    $scope.saveCardAndRequestBooking(null);
                }

            };

            /**
             * Save payment info and request product booking.
             */
            $scope.saveCardAndRequestBooking = function (defaultAddress) {
                if (defaultAddress) {
                    $scope.currentUser.default_address = defaultAddress;
                    UsersService.updateUser({default_address: Endpoints.api_url + "addresses/" + defaultAddress.id + "/"});
                }
                $scope.submitInProgress = true;
                // Update user info
                var userPatch = {};
                userPatch.first_name = $scope.currentUser.first_name;
                userPatch.last_name = $scope.currentUser.last_name;
                if ($scope.isAuto) {
                    userPatch.drivers_license_number = $scope.currentUser.drivers_license_number;
                    if ($scope.currentUser.drivers_license_date) {
                        userPatch.drivers_license_date = UtilsService.formatDate($scope.currentUser.drivers_license_date, "yyyy-MM-dd'T'HH:mm");
                    }
                    userPatch.place_of_birth = $scope.currentUser.place_of_birth;
                    if ($scope.currentUser.date_of_birth) {
                        userPatch.date_of_birth = UtilsService.formatDate($scope.currentUser.date_of_birth, "yyyy-MM-dd'T'HH:mm");
                    }
                }

                UsersService.updateUser(userPatch).then(function (result) {
                    // Update credit card info
                    $scope.creditCard.expires = $scope.creditCard.expires.replace("/", "");
                    // If credit card exists now it is deleted and saved again
                    if ($scope.creditCard.masked_number === "") {
                        if (!!$scope.creditCard.id) {
                            CreditCardsService.deleteCard($scope.creditCard).then(function () {
                                $scope.saveCreditCard();
                            });
                        } else {
                            $scope.saveCreditCard();
                        }
                    } else {
                        $scope.requestBooking();
                    }
                }, function (error) {
                    $scope.handleResponseErrors(error);
                });
            };

            $scope.saveCreditCard = function () {
                CreditCardsService.saveCard($scope.creditCard).then(
                    $scope.requestBooking(),
                    $scope.handleResponseErrors
                );
            };

            /**
             * Save booking and make payment request.
             */
            $scope.requestBooking = function () {
                var booking = {},
                    fromDateTimeStr = $scope.bookingDetails.fromDate + " " + $scope.bookingDetails.fromHour.value,
                    toDateTimeStr = $scope.bookingDetails.toDate + " " + $scope.bookingDetails.toHour.value,
                    fromDateTime = Date.parseExact(fromDateTimeStr, "dd/MM/yyyy HH:mm:ss"),
                    toDateTime = Date.parseExact(toDateTimeStr, "dd/MM/yyyy HH:mm:ss");
                booking.started_at = fromDateTime.toString("yyyy-MM-ddTHH:mm");
                booking.ended_at = toDateTime.toString("yyyy-MM-ddTHH:mm");
                booking.owner = Endpoints.api_url + "users/" + $scope.product.owner.id + "/";
                booking.borrower = Endpoints.api_url + "users/" + $scope.currentUser.id + "/";
                booking.product = Endpoints.api_url + "products/" + $scope.product.id + "/";
                // Create booking
                BookingsService.requestBooking(booking).then(
                    $scope.processBookingResponse,
                    $scope.handleResponseErrors
                );
            };

            $scope.processBookingResponse = function (booking) {
                var paymentInfo = {}, selectedPoint = {};
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
                angular.forEach($scope.borrowerShippingPoints, function (value) {
                    if ($scope.selectedPointId === value.site_id) {
                        selectedPoint = value;
                    }
                });
                if (!!selectedPoint && !!selectedPoint.site_id) {
                    selectedPoint.type = 2;
                    selectedPoint.booking = Endpoints.api_url + "bookings/" + booking.uuid + "/";
                    selectedPoint.patron = Endpoints.api_url + "users/" + $scope.currentUser.id + "/";
                    PatronShippingPointsService.saveShippingPoint(selectedPoint).then(function () {
                        $scope.payForBooking(booking, paymentInfo);
                    }, function (error) {
                        $scope.handleResponseErrors(error);
                    });
                } else {
                    $scope.payForBooking(booking, paymentInfo);
                }
            };

            $scope.payForBooking = function (booking, paymentInfo) {
                BookingsService.payForBooking(booking.uuid, paymentInfo).then(
                    function () {
                        $scope.processBookingPaymentResponse(booking);
                    },
                    $scope.handleResponseErrors
                );
            };

            $scope.processBookingPaymentResponse = function (booking) {
                ScriptTagService.loadAdWordsTags("-XHsCMvspQMQjaaF6gM");
                ScriptTagService.trackEvent("Réservation", "Demande de réservation", $scope.getEventLabel());
                ScriptTagService.trackPageView();
                toastr.options.positionClass = "toast-top-full-width";
                toastr.success("Réservation enregistré");
                $(".modal").modal("hide");
                //$window.location.href = "/dashboard/#/bookings/" + booking.uuid;
                $scope.submitInProgress = false;
                ToDashboardRedirectService.showPopupAndRedirect("/dashboard/#/bookings/" + booking.uuid);
            };

            /**
             * Get label for google analytics event base on product category.
             * @returns event tag label
             */
            $scope.getEventLabel = function () {
                if ($scope.isAuto) {
                    return "Voiture - " + $scope.productCategoryName;
                }
                if ($scope.isRealEstate) {
                    return "Logement - " + $scope.productCategoryName;
                }
                return "Objet - " + $scope.productCategoryAncestors;
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
                $scope.openModal("login");
            });

            /**
             * Load necessary data on modal window open event based on modal name.
             */
            $scope.$on("openModal", function (event, args) {
                $scope.openModal(args.name);
            });

            $scope.openModal = function (name) {
                var currentUserToken = AuthService.getUserToken(), modalContainer;
                if (!currentUserToken && name !== "login") {
                    AuthService.saveAttemptUrl(name);
                    name = "login";
                } else {
                    if ((name === "message") && $scope.productRelatedMessages.length === 0) {
                        $scope.loadMessageThread();
                    } else if (name === "booking") {
                        $scope.loadCreditCards();
                        $scope.loadProductShippingPoint();
                    } else if (name === "phone") {
                        $scope.loadPhoneDetails();
                    }
                }
                if (name !== "login") {
                    if ($scope.currentUser && !$scope.currentUser.default_address) {
                        $scope.noAddress = true;
                    }
                    if (!$scope.product) {
                        ProductsService.getProduct($scope.productId, false, false).then(function (result) {
                            $scope.product = result;
                            $scope.loadPictures();
                            $scope.loadProductCategoryAncestors(name);
                        });
                    } else {
                        $scope.loadPictures();
                        $scope.loadProductCategoryAncestors(name);
                    }
                }

                if (name) {
                    $(".modal").modal("hide");
                    modalContainer = $("#" + name + "Modal");
                    modalContainer.modal("show");
                }
            };

            /**
             * Loads all ancestors of product category for analytics tags.
             * @param modalName name of modal window
             */
            $scope.loadProductCategoryAncestors = function (modalName) {
                $scope.productCategoryName = $scope.product.category.name;
                CategoriesService.getAncestors($scope.product.category.id).then(function (ancestors) {
                    $scope.applyProductCategoryAncestors(ancestors, modalName);
                });
            };

            $scope.applyProductCategoryAncestors = function (ancestors, modalName) {
                var categoriesStr = "";
                angular.forEach(ancestors, function (value) {
                    categoriesStr = categoriesStr + value.name + " - ";
                });
                $scope.productCategoryAncestors = categoriesStr + $scope.product.category.name;
                if (modalName === "phone") {
                    ScriptTagService.trackEvent("Réservation", "Appel", $scope.getEventLabel());
                    ScriptTagService.trackPageView();
                }
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
                var currentPath = $location.path(),
                    newPath = currentPath.slice(0, currentPath.indexOf(args.name));
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
                        phoneId = $scope.product.phone.id;
                    }
                }
                if (phoneId) {
                    PhoneNumbersService.getPremiumRateNumber(phoneId).then(
                        $scope.applyPremiumRateNumberResponse
                    );
                } else {
                    $scope.ownerCallDetailsError = "Le numero n'est pas disponible";
                }
            };

            $scope.applyPremiumRateNumberResponse = function (result) {
                if (!result.error || result.error === "0") {
                    $scope.ownerCallDetails = {
                        number: result.numero,
                        tariff: result.tarif
                    };
                } else {
                    $scope.ownerCallDetailsError = !!result.error_msg ? result.error_msg : "Le numero n'est pas disponible";
                }
            };

            /**
             * Parses user creadit card info.
             */
            $scope.loadCreditCards = function () {
                if (!$scope.currentUserPromise) {
                    $scope.currentUserPromise = UsersService.getMe();
                }
                $scope.currentUserPromise.then($scope.applyUserCreditCard);
            };

            $scope.applyUserCreditCard = function (currentUser) {
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
            };

            $scope.loadProductShippingPoint = function () {
                $scope.currentUserPromise.then(function (currentUser) {
                    $scope.currentUser = currentUser;
                    $scope.loadingProductShippingPoint = true;
                    ProductShippingPointsService.getByProduct($scope.productId).then(
                        $scope.applyProductShippingPoint,
                        $scope.handleResponseErrors
                    );
                });
            };

            $scope.applyProductShippingPoint = function (data) {
                //Show shipping choice only if there are existing product shipping points
                if (!!data.results && data.results.length > 0) {
                    $scope.productShippingPoint = data.results[0];
                    $scope.shippingAllowed = true;
                }
                $scope.loadingProductShippingPoint = false;
            };

            $scope.loadShippingPoints = function () {
                if ($scope.addShipping && $scope.borrowerShippingPoints.length === 0) {
                    if ($scope.currentUser.default_address) {
                        $scope.shippingPointsRequestInProgress = true;
                        var shippingPointsPromise = {}, addressString;
                        if (!$scope.currentUser.default_address.position) {
                            addressString = $scope.currentUser.default_address.zipcode + " " + $scope.currentUser.default_address.street + " " + $scope.currentUser.default_address.city;
                            shippingPointsPromise = ShippingPointsService.searchArrivalShippingPointsByAddressAndProduct(addressString, $scope.productId);
                        } else {
                            shippingPointsPromise = ShippingPointsService.searchArrivalShippingPointsByCoordinatesAndProduct($scope.currentUser.default_address.position.coordinates[0], $scope.currentUser.default_address.position.coordinates[1], $scope.productId);
                        }
                        shippingPointsPromise.then(
                            $scope.applyArrivalShippingPoint,
                            $scope.handleResponseErrors
                        );
                    }
                }
                if (!$scope.addShipping) {
                    $scope.shippingPrice = 0;
                    $scope.selectedPointId = "";
                }
            };

            $scope.applyArrivalShippingPoint = function (result) {
                $scope.shippingPointsRequestInProgress = false;
                //TODO: it's temperory, then will call pricing service
                angular.forEach(result, function (value) {
                    value.price = "10.0";
                });
                $scope.borrowerShippingPoints = result;
                $("#point-contatiner").mCustomScrollbar({
                    scrollInertia: "100",
                    autoHideScrollbar: false,
                    theme: "dark-thin",
                    advanced: {
                        updateOnContentResize: true,
                        autoScrollOnFocus: false
                    }
                });
            };

            /**
             * Loads message thread for send message to owner modal window.
             */
            $scope.loadMessageThread = function () {
                if (!$scope.currentUserPromise) {
                    $scope.currentUserPromise = UsersService.getMe();
                }
                $scope.currentUserPromise.then(function (currentUser) {
                    // Save current user in the scope
                    $scope.currentUser = currentUser;
                    MessageThreadsService.getMessageThreadByProductAndParticipant($scope.productId, $scope.currentUser.id).then($scope.applyMessageThread);
                });
            };

            $scope.applyMessageThread = function (result) {
                angular.forEach(result, function (value) {
                    $scope.threadId = UtilsService.getIdFromUrl(value.thread);
                });
                $scope.productRelatedMessages = result;
            };

            $scope.applyDatePicker = function (fieldId) {
                $("#" + fieldId).datepicker({
                    language: "fr",
                    autoclose: true,
                    todayHighlight: true,
                    dateFormat: "yyyy-MM-dd"
                });
            };
            $scope.applyDatePicker("date_of_birth");
            $scope.applyDatePicker("drivers_license_date");
        }]);
});
