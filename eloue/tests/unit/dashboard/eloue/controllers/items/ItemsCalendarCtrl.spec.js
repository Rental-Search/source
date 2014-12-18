define(["angular-mocks", "datejs", "eloue/controllers/items/ItemsCalendarCtrl", "datejs"], function () {

    describe("Controller: ItemsCalendarCtrl", function () {

        var ItemsCalendarCtrl,
            scope,
            stateParams,
            endpointsMock,
            bookingsServiceMock,
            unavailabilityPeriodsServiceMock;

        beforeEach(module('EloueDashboardApp'));

        beforeEach(function () {
            endpointsMock = {};

            bookingsServiceMock = {
                getBookingsByProduct: function (productId) {
                    console.log("bookingsServiceMock:getBookingsByProduct called with productId = " + productId);
                    return {
                        then: function () {
                            return {response: {}}
                        }
                    }
                }
            };

            unavailabilityPeriodsServiceMock = {
                savePeriod: function (period) {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                },

                updatePeriod: function (period) {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                },

                deletePeriod: function (period) {
                    return {
                        $promise: {
                            then: function () {
                                return {result: {}}
                            }
                        }
                    }
                },

                getByProduct: function (productId) {
                    return {
                        then: function () {
                            return {response: {}}
                        }
                    }
                }
            };

            module(function ($provide) {
                $provide.value("Endpoints", endpointsMock);
                $provide.value("BookingsService", bookingsServiceMock);
                $provide.value("UnavailabilityPeriodsService", unavailabilityPeriodsServiceMock);
            })
        });

        beforeEach(inject(function ($rootScope, $controller) {
            scope = $rootScope.$new();
            stateParams = {
                id: 1
            };

            spyOn(bookingsServiceMock, "getBookingsByProduct").and.callThrough();
            spyOn(unavailabilityPeriodsServiceMock, "savePeriod").and.callThrough();
            spyOn(unavailabilityPeriodsServiceMock, "updatePeriod").and.callThrough();
            spyOn(unavailabilityPeriodsServiceMock, "deletePeriod").and.callThrough();
            spyOn(unavailabilityPeriodsServiceMock, "getByProduct").and.callThrough();

            ItemsCalendarCtrl = $controller('ItemsCalendarCtrl', {
                $scope: scope,
                $stateParams: stateParams,
                Endpoints: endpointsMock,
                BookingsService: bookingsServiceMock,
                UnavailabilityPeriodsService: unavailabilityPeriodsServiceMock
            });
            expect(bookingsServiceMock.getBookingsByProduct).toHaveBeenCalled();
        }));

        it("ItemsCalendarCtrl should be not null", function () {
            expect(!!ItemsCalendarCtrl).toBe(true);
        });

        it("ItemsCalendarCtrl:updateCalendar", function () {
            scope.selectedMonthAndYear = Date.today().getMonth() + " " + Date.today().getFullYear();
            scope.updateCalendar();
        });

        it("ItemsCalendarCtrl:updateUnavailabilityPeriods", function () {
            scope.updateUnavailabilityPeriods();
            expect(unavailabilityPeriodsServiceMock.getByProduct).toHaveBeenCalledWith(stateParams.id);
        });

        it("ItemsCalendarCtrl:saveUnavailabilityPeriod", function () {
            scope.newUnavailabilityPeriod = {
                "quantity": 1,
                "started_at": "06/12/2014",
                "ended_at": "08/12/2014"
            };
            scope.saveUnavailabilityPeriod();
            expect(unavailabilityPeriodsServiceMock.savePeriod).toHaveBeenCalled();
        });

        it("ItemsCalendarCtrl:validateUnavailabilityPeriod", function () {
            var startDate = new Date(), endDate = new Date();
            var result = scope.validateUnavailabilityPeriod(startDate, endDate);
            expect(result).toBeTruthy();
        });

        it("ItemsCalendarCtrl:deleteUnavailabilityPeriod", function () {
            var period = { id: 1};
            scope.deleteUnavailabilityPeriod(period);
            expect(unavailabilityPeriodsServiceMock.deletePeriod).toHaveBeenCalledWith(period);
        });
    });
});