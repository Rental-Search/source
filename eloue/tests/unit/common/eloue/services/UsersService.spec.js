define(["angular-mocks", "eloue/commonApp", "eloue/services"], function () {

    describe("Service: UsersService", function () {

        var UsersService,
            usersMock,
            formServiceMock,
            endpointsMock;

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            usersMock = {
                get: function () {
                },
                getMe: function () {
                },
                getStats: function () {
                }
            };
            formServiceMock = {
                send: function (method, currentUserUrl, form, successCallback, errorCallback) {
                }
            };
            endpointsMock = {};

            module(function ($provide) {
                $provide.value("Users", usersMock);
                $provide.value("FormService", formServiceMock);
                $provide.value("Endpoints", endpointsMock);
            });
        });

        beforeEach(inject(function (_UsersService_) {
            UsersService = _UsersService_;
            spyOn(usersMock, "get").andCallThrough();
            spyOn(usersMock, "getMe").andCallThrough();
            spyOn(usersMock, "getStats").andCallThrough();
            spyOn(formServiceMock, "send").andCallThrough();
        }));

        it("UsersService should be not null", function () {
            expect(!!UsersService).toBe(true);
        });

        it("UsersService:get", function () {
            var userId = 1;
            UsersService.get(userId);
            expect(usersMock.get).toHaveBeenCalledWith({id: userId}, undefined, undefined);
        });

        it("UsersService:getMe", function () {
            UsersService.getMe();
            expect(usersMock.getMe).toHaveBeenCalledWith(jasmine.any(Object), undefined, undefined);
        });

        it("UsersService:getStatistics", function () {
            var userId = 1;
            UsersService.getStatistics(userId);
            expect(usersMock.getStats).toHaveBeenCalledWith({id: userId, _cache: jasmine.any(Number)});
        });

        it("UsersService:sendForm", function () {
            var userId = 1;
            UsersService.sendForm(userId);
            expect(formServiceMock.send).toHaveBeenCalled();
        });

        it("UsersService:resetPassword", function () {
            var userId = 1;
            UsersService.resetPassword(userId);
            expect(formServiceMock.send).toHaveBeenCalled();
        });
    });
});
