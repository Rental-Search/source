define(["../../../common/eloue/commonApp", "../../../common/eloue/resources", "../../../common/eloue/values",
    "../../../common/eloue/services/FormService"], function (EloueCommon) {
    "use strict";
    /**
     * Service for managing pictures.
     */
    EloueCommon.factory("PicturesService", ["Pictures", "Endpoints", "FormService", function (Pictures, Endpoints, FormService) {
        var picturesService = {};

        picturesService.savePicture = function (form, successCallback, errorCallback) {
            // Calculate current user url
            var url = Endpoints.api_url + "pictures/";

            // Send form to the url
            FormService.send("POST", url, form, successCallback, errorCallback);
        };

        picturesService.deletePicture = function (pictureId) {
            return Pictures.delete({id: pictureId}).$promise;
        };

        return picturesService;
    }]);
});
