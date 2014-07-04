define(["app"], function (eloueApp) {

    'use strict';

    eloueApp.value('Endpoints', [
        {
            key: 'oauth_url',
            value: 'http://10.0.0.111:8000/oauth2'
        },
        {
            key: 'api_url',
            value: 'http://10.0.0.111:8000/api/2.0/'
        }
    ]);

});