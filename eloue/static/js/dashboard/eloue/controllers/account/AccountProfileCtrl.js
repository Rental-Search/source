"use strict";

define(["angular", "eloue/app"], function (angular) {

    /**
     * Controller for the account's profile page.
     */
    angular.module("EloueDashboardApp").controller("AccountProfileCtrl", [
        "$scope",
        "UsersService",
        "AddressesService",
        "PhoneNumbersService",
        "Endpoints",
        "CivilityChoices",
        function ($scope, UsersService, AddressesService, PhoneNumbersService, Endpoints, CivilityChoices) {
            $scope.civilityOptions = CivilityChoices;
            $scope.addressesBaseUrl = Endpoints.api_url + "addresses/";
            $scope.phonesBaseUrl = Endpoints.api_url + "phones/";
            $scope.usersBaseUrl = Endpoints.api_url + "users/";
            $scope.markListItemAsSelected("account-part-", "account.profile");

            $scope.currentUserPromise.then(function (currentUser) {
                // Save current user in the scope
                $scope.currentUser = currentUser;
                if (!!$scope.currentUser.default_number) {
                    $scope.phoneNumber = !!$scope.currentUser.default_number.number.numero ? $scope.currentUser.default_number.number.numero : $scope.currentUser.default_number.number;
                }
                AddressesService.getAddressesByPatron(currentUser.id).$promise.then(function (data) {
                    $scope.addressList = data.results;
                    $scope.defaultAddress = (!!currentUser.default_address) ? $scope.addressesBaseUrl + currentUser.default_address.id + "/" : null;
                    console.log($scope.defaultAddress);
                });

                console.log($scope.currentUser);
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
                var initialNumber = !!$scope.currentUser.default_number ? (!!$scope.currentUser.default_number.number.numero ? $scope.currentUser.default_number.number.numero : $scope.currentUser.default_number.number) : null;
                if ($scope.phoneNumber != initialNumber) {
                    if (!initialNumber) {
                        $scope.saveNewPhone();
                    } else {
                        PhoneNumbersService.deletePhoneNumber($scope.currentUser.default_number.id).$promise.then(function (result) {
                            $scope.saveNewPhone();
                        });
                    }
                } else {
                    if (!!$scope.currentUser.default_number) {
                        $scope.currentUser.default_number = $scope.phonesBaseUrl + $scope.currentUser.default_number.id + "/";
                    }
                    $scope.sendUserForm();
                }
            };

            $scope.saveNewPhone = function() {
                var newPhone = {
                    patron: $scope.usersBaseUrl + $scope.currentUser.id + "/",
                    number: $scope.phoneNumber
                };
                PhoneNumbersService.savePhoneNumber(newPhone).$promise.then(function (number) {
                    $scope.currentUser.default_number = $scope.phonesBaseUrl + number.id + "/";
                    $("#phone_number").val($scope.currentUser.default_number);
                    $scope.sendUserForm();
                })
            };

            $scope.sendUserForm = function () {
                UsersService.sendForm($scope.currentUser.id, $("#profile-information"), function (data) {
                    $scope.$apply(function () {
                        $scope.submitInProgress = false;
                    });
                });
            }
        }
    ]);
});