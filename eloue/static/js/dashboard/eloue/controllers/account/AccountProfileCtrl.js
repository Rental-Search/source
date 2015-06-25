define([
    "eloue/app",
    "../../../../common/eloue/values",
    "../../../../common/eloue/services/UsersService",
    "../../../../common/eloue/services/AddressesService",
    "../../../../common/eloue/services/PhoneNumbersService"
], function (EloueDashboardApp) {
    "use strict";
    /**
     * Controller for the account's profile page.
     */
    EloueDashboardApp.controller("AccountProfileCtrl", [
        "$scope",
        "$timeout",
        "UsersService",
        "AddressesService",
        "PhoneNumbersService",
        "Endpoints",
        "CivilityChoices",
        "UtilsService",
        function ($scope, $timeout, UsersService, AddressesService, PhoneNumbersService, Endpoints, CivilityChoices,
                  UtilsService) {
            $scope.civilityOptions = CivilityChoices;
            $scope.addressesBaseUrl = Endpoints.api_url + "addresses/";
            $scope.phonesBaseUrl = Endpoints.api_url + "phones/";
            $scope.usersBaseUrl = Endpoints.api_url + "users/";
            $scope.dayOptions = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31"];
            $scope.monthOptions = [
                {id: 0, value: "January"},
                {id: 1, value: "February"},
                {id: 2, value: "March"},
                {id: 3, value: "April"},
                {id: 4, value: "May"},
                {id: 5, value: "June"},
                {id: 6, value: "July"},
                {id: 7, value: "August"},
                {id: 8, value: "September"},
                {id: 9, value: "October"},
                {id: 10, value: "November"},
                {id: 11, value: "December"}
            ];
            $scope.yearOptions = [];
            var currentYear = Date.today().getFullYear(), i;
            for (i = 0; i < 99; i += 1) {
                $scope.yearOptions.push(currentYear - i);
            }
            $scope.licenceDay = null;
            $scope.licenceMonth = null;
            $scope.licenceYear = null;

            $scope.markListItemAsSelected("account-part-", "account.profile");

            $scope.handleResponseErrors = function (error, object, action) {
                $timeout(function () {
                    $scope.submitInProgress = false;
                }, 0);
                $scope.showNotification(object, action, false);
            };

            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe();
            }
            $scope.currentUserPromise.then(function (currentUser) {
                $scope.applyUserDetails(currentUser);
            });

            $scope.applyUserDetails = function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;
                if ($scope.currentUser.default_number) {
                    $scope.phoneNumber = $scope.currentUser.default_number.number.numero || $scope.currentUser.default_number.number;
                }
                if (!currentUser.default_address) {
                    $scope.noAddress = true;
                }
                if (!$scope.noAddress) {
                    AddressesService.getAddressesByPatron(currentUser.id).then(function (results) {
                        $scope.addressList = results;
                        $scope.defaultAddress = currentUser.default_address ? $scope.addressesBaseUrl + currentUser.default_address.id + "/" : null;
                        // Timeout is used because of chosen issue (when options are loaded asynchronously, they sometimes not visible in chosen widget)
                        $timeout(function () {
                            $("#defaultAddressSelect").chosen();
                        }, 200);
                    });
                }
                if ($scope.currentUser.drivers_license_date) {
                    var licenceDate = Date.parse($scope.currentUser.drivers_license_date);
                    $scope.licenceDay = licenceDate.getDate();
                    $scope.licenceMonth = licenceDate.getMonth();
                    $scope.licenceYear = licenceDate.getFullYear();
                }
                $scope.initCustomScrollbars();
            };

            // Send form when a file changes
            $scope.onFileChanged = function () {
                UsersService.sendForm($scope.currentUser.id, $("#change-photo"), function (data) {
                    $scope.$apply(function () {
                        $scope.currentUser.avatar = data.avatar;
                    });
                    analytics.track('User Picture Updated');
                });
            };

            // Send form with data by submit
            $scope.dataFormSubmit = function () {
                $scope.submitInProgress = true;
                if ($scope.noAddress) {
                    $scope.currentUser.default_address.country = "FR";
                    AddressesService.saveAddress($scope.currentUser.default_address).then(
                        $scope.processAddressSaveResponse,
                        function (error) {
                            $scope.handleResponseErrors(error, "profile", "save");
                        }
                    );
                } else {
                    $scope.saveProfile();
                }
            };

            $scope.processAddressSaveResponse = function (result) {
                $scope.currentUser.default_address = result;
                $scope.defaultAddress = $scope.currentUser.default_address;
                $scope.noAddress = false;
                UsersService.updateUser({default_address: Endpoints.api_url + "addresses/" + result.id + "/"}).then(function () {
                    AddressesService.getAddressesByPatron($scope.currentUser.id).then(function (results) {
                        $scope.addressList = results;
                        $timeout(function () {
                            $("#defaultAddressSelect").chosen();
                        }, 200);
                    });
                });
                $scope.saveProfile();
            };

            $scope.saveProfile = function () {
                if (!!$scope.licenceDay && !!$scope.licenceMonth && !!$scope.licenceYear) {
                    var date = new Date();
                    date.setDate($scope.licenceDay);
                    date.setMonth($scope.licenceMonth);
                    date.setFullYear($scope.licenceYear);
                    $scope.currentUser.drivers_license_date = date.toString("yyyy-MM-ddTHH:mm");
                    $("#drivers_license_date").val($scope.currentUser.drivers_license_date);
                }
                var initialNumber = $scope.currentUser.default_number ? ($scope.currentUser.default_number.number.numero || $scope.currentUser.default_number.number) : null;
                if ($scope.phoneNumber != initialNumber) {
                    if (!initialNumber) {
                        $scope.saveNewPhone();
                    } else {
                        $scope.currentUser.default_number.number = $scope.phoneNumber;
                        PhoneNumbersService.updatePhoneNumber($scope.currentUser.default_number).then(function (number) {
                            $("#default_number").val($scope.phonesBaseUrl + number.id + "/");
                            $scope.sendUserForm();
                        }, function (error) {
                            $scope.handleResponseErrors(error, "profile", "save");
                        });
                    }
                } else {
                    if ($scope.currentUser.default_number) {
                        $("#default_number").val($scope.phonesBaseUrl + $scope.currentUser.default_number.id + "/");
                    }
                    $scope.sendUserForm();
                }
            };

            $scope.saveNewPhone = function () {
                var newPhone = {
                    patron: $scope.usersBaseUrl + $scope.currentUser.id + "/",
                    number: $scope.phoneNumber
                };
                PhoneNumbersService.savePhoneNumber(newPhone).then(function (number) {
                    $("#default_number").val($scope.phonesBaseUrl + number.id + "/");
                    $scope.sendUserForm();
                }, function (error) {
                    $scope.handleResponseErrors(error, "profile", "save");
                });
            };

            $scope.sendUserForm = function () {
                UsersService.sendForm($scope.currentUser.id, $("#profileInformation"), function (data) {
                    analytics.identify(data.id, {
                        'email': data.email,
                        'firstName': data.first_name,
                        'lastName': data.last_name,
                        'name': data.first_name + " " + data.last_name,
                        'username': data.username,
                        'newsletter': data.is_subscribed,
                    });
                    analytics.track('User Profile Updated');
                    $scope.$apply(function () {
                        $scope.submitInProgress = false;
                        $scope.showNotificationMessage(UtilsService.translate("informationHasBeenUpdated"), true);
                    });
                }, function (error) {
                    $scope.handleResponseErrors(error.responseJSON, "profile", "save");
                });
            };
        }
    ]);
});
