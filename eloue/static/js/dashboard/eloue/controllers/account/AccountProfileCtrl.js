"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's profile page.
     */
    angular.module("EloueDashboardApp").controller("AccountProfileCtrl", [
        "$scope",
        "$timeout",
        "UsersService",
        "AddressesService",
        "PhoneNumbersService",
        "Endpoints",
        "CivilityChoices",
        function ($scope, $timeout, UsersService, AddressesService, PhoneNumbersService, Endpoints, CivilityChoices) {
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
            var currentYear = Date.today().getFullYear();
            for (var i = 0; i < 99; i++) {
                $scope.yearOptions.push(currentYear - i);
            }
            $scope.licenceDay =  null;
            $scope.licenceMonth = null;
            $scope.licenceYear = null;

            $scope.markListItemAsSelected("account-part-", "account.profile");
            $scope.errors = {
                is_professional: "",
                username: "",
                email: "",
                first_name: "",
                last_name: "",
                default_address: "",
                default_number: "",
                about: "",
                is_subscribed: "",
                drivers_license_date: "",
                drivers_license_number: ""
            };

            $scope.handleResponseErrors = function(error) {
                if (!!error.errors) {
                    $scope.errors = {
                        is_professional: !!error.errors.is_professional ? error.errors.is_professional[0] : "",
                        username: !!error.errors.username ? error.errors.username[0] : "",
                        email: !!error.errors.email ? error.errors.email[0] : "",
                        first_name: !!error.errors.first_name ? error.errors.first_name[0] : "",
                        last_name: !!error.errors.last_name ? error.errors.last_name[0] : "",
                        default_address: !!error.errors.default_address ? error.errors.default_address[0] : "",
                        default_number: !!error.errors.default_number ? error.errors.default_number[0] : "",
                        about: !!error.errors.about ? error.errors.about[0] : "",
                        is_subscribed: !!error.errors.is_subscribed ? error.errors.is_subscribed[0] : "",
                        drivers_license_date: !!error.errors.drivers_license_date ? error.errors.drivers_license_date[0] : "",
                        drivers_license_number: !!error.errors.drivers_license_number ? error.errors.drivers_license_number[0] : ""
                    };
                }
                $scope.$apply(function () {
                    $scope.submitInProgress = false;
                });

            };

            if (!$scope.currentUserPromise) {
                $scope.currentUserPromise = UsersService.getMe().$promise;
            }
            $scope.currentUserPromise.then(function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;
                if (!!$scope.currentUser.default_number) {
                    $scope.phoneNumber = !!$scope.currentUser.default_number.number.numero ? $scope.currentUser.default_number.number.numero : $scope.currentUser.default_number.number;
                }
                AddressesService.getAddressesByPatron(currentUser.id).then(function (results) {
                    $scope.addressList = results;
                    $scope.defaultAddress = (!!currentUser.default_address) ? $scope.addressesBaseUrl + currentUser.default_address.id + "/" : null;
                    $timeout(function () {
                        $("#defaultAddressSelect").chosen();
                    }, 200);
                });
                if (!!$scope.currentUser.drivers_license_date) {
                    var licenceDate = Date.parse($scope.currentUser.drivers_license_date);
                    $scope.licenceDay =  licenceDate.getDate();
                    $scope.licenceMonth = licenceDate.getMonth();
                    $scope.licenceYear = licenceDate.getFullYear();
                }
                $scope.initCustomScrollbars();
            });

            // Send form when a file changes
            $scope.onFileChanged = function () {
                UsersService.sendForm($scope.currentUser.id, $("#change-photo"), function (data) {
                    $scope.$apply(function () {
                        $scope.currentUser.avatar = data.avatar;
                    });
                });
            };

            // Send form with data by submit
            $scope.dataFormSubmit = function () {
                $scope.submitInProgress = true;
                if (!!$scope.licenceDay && !!$scope.licenceMonth && !!$scope.licenceYear) {
                    var date = new Date();
                    date.setDate($scope.licenceDay);
                    date.setMonth($scope.licenceMonth);
                    date.setFullYear($scope.licenceYear);
                    $scope.currentUser.drivers_license_date = date.toString("yyyy-MM-ddTHH:mm");
                    $("#drivers_license_date").val($scope.currentUser.drivers_license_date);
                }
                var initialNumber = !!$scope.currentUser.default_number ? (!!$scope.currentUser.default_number.number.numero ? $scope.currentUser.default_number.number.numero : $scope.currentUser.default_number.number) : null;
                if ($scope.phoneNumber != initialNumber) {
                    if (!initialNumber) {
                        $scope.saveNewPhone();
                    } else {
                        $scope.currentUser.default_number.number = $scope.phoneNumber;
                        PhoneNumbersService.updatePhoneNumber($scope.currentUser.default_number).$promise.then(function (number) {
                            $("#default_number").val($scope.phonesBaseUrl + number.id + "/");
                            $scope.sendUserForm();
                        }, function (error) {
                            $scope.handleResponseErrors(error);
                        });
                    }
                } else {
                    if (!!$scope.currentUser.default_number) {
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
                PhoneNumbersService.savePhoneNumber(newPhone).$promise.then(function (number) {
                    $("#default_number").val($scope.phonesBaseUrl + number.id + "/");
                    $scope.sendUserForm();
                }, function (error) {
                    $scope.handleResponseErrors(error);
                })
            };

            $scope.sendUserForm = function () {
                UsersService.sendForm($scope.currentUser.id, $("#profile-information"), function (data) {
                    $scope.$apply(function () {
                        $scope.submitInProgress = false;
                    });
                }, function (error) {
                    $scope.handleResponseErrors(error.responseJSON);
                });
            }
        }
    ]);
});