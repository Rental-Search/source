define(["angular-mocks", "eloue/services/UsersService"], function () {

    describe("Service: UsersService", function () {

        var UsersService,
            q,
            usersMock,
            formServiceMock,
            endpointsMock,
            simpleResourceResponse = {
                $promise: {
                    then: function () {
                        return {results: []};
                    }
                }
            };

        beforeEach(module("EloueCommon"));

        beforeEach(function () {
            usersMock = {
                get: function () {
                    return simpleResourceResponse;
                },
                getMe: function () {
                    return simpleResourceResponse;
                },
                getStats: function () {
                    return simpleResourceResponse;
                },
                update: function (id, user) {
                    return simpleResourceResponse;
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

        beforeEach(inject(function (_UsersService_, $q) {
            UsersService = _UsersService_;
            q = $q;
            spyOn(usersMock, "get").and.callThrough();
            spyOn(usersMock, "getMe").and.callThrough();
            spyOn(usersMock, "getStats").and.callThrough();
            spyOn(usersMock, "update").and.callThrough();
            spyOn(formServiceMock, "send").and.callThrough();
        }));

        it("UsersService should be not null", function () {
            expect(!!UsersService).toBe(true);
        });

        it("UsersService:get", function () {
            var userId = 1;
            UsersService.get(userId);
            expect(usersMock.get).toHaveBeenCalledWith({id: userId, _cache: jasmine.any(Number)}, undefined, undefined);
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

        it("UsersService:updateUser", function () {
            var user = {
                id: 1
            };
            UsersService.updateUser(user);
            expect(usersMock.update).toHaveBeenCalledWith({id: "me"}, user);
        });
    });
});
