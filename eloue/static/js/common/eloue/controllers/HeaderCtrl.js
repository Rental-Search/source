define([
    'eloue/app'
], function (EloueWidgetsApp) {
    'use strict';
    /**
     * Controller to run scripts necessary for the site header.
     */
    EloueWidgetsApp.controller('HeaderCtrl', [
        '$scope',
        function ($scope) {
            var fromDateSelector = $("input[name='date_from']"),
                toDateSelector = $("input[name='date_to']");

            $scope.activateDatePicker = function() {
                if (!fromDateSelector || !toDateSelector) {
                    return;
                }
                fromDateSelector.datepicker({
                    language: 'fr',
                    autoclose: true,
                    startDate: Date.today().add(1).days().toString('dd/MM/yyyy')
                });
                toDateSelector.datepicker({
                    language: 'fr',
                    autoclose: true,
                    startDate: Date.today().add(2).days().toString('dd/MM/yyyy')
                });
            };

            $scope.validateDates = function() {
                // If only one date was provided, do nothing.
                if (!$scope.fromDate || !$scope.toDate) {
                    return;
                }

                var fromDate = Date.parseExact($scope.fromDate, 'dd/MM/yyyy'),
                    toDate = Date.parseExact($scope.toDate, 'dd/MM/yyyy');

                // If 'to date' is before 'from date', then set 'to date' as 'from date' plus 1 day.
                if (fromDate >= toDate) {
                    toDateSelector.datepicker('setDate', fromDate.add(1).days());
                }
            };

            $scope.activateDatePicker();
        }]);
});
