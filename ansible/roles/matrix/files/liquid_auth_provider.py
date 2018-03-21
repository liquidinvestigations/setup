# Based on https://github.com/kamax-io/matrix-synapse-rest-auth
# Copyright (C) 2017 Maxime Dor

import logging
from twisted.internet import defer
import requests

logger = logging.getLogger('synapse.liquid_auth_provider')

class RestAuthProvider(object):

    def __init__(self, config, account_handler):
        self.account_handler = account_handler
        self.endpoint = config['endpoint']
        logger.info('Endpoint: %s', self.endpoint)

    @defer.inlineCallbacks
    def check_password(self, user_id, password):
        logger.info("Got password check for " + user_id)

        profile_url = self.endpoint + '/accounts/profile'
        profile_resp = requests.get(profile_url, headers={
            'Authorization': 'Bearer {}'.format(password),
        })

        if profile_resp.status_code != 200:
            logger.warn('auth fail - profile response: %r', profile_resp)
            defer.returnValue(False)

        profile = profile_resp.json()
        if not profile:
            logger.warn('auth fail - empty profile: %r', profile)
            defer.returnValue(False)

        logger.warn("LIQUID LOGIN OK! %r", profile)

        localpart = user_id.split(":", 1)[0][1:]
        if localpart != profile['login']:
            raise RuntimeError("User localpart mismatch (%r)" %
                               [user_id, profile['login']])

        logger.info("User %s authenticated", user_id)

        if not (yield self.account_handler.check_user_exists(user_id)):
            logger.info("User %s does not exist yet, creating...", user_id)

            if localpart != localpart.lower():
                logger.info('User %s was cannot be created due to username '
                            'lowercase policy', localpart)
                defer.returnValue(False)

            user_id, access_token = (yield self.account_handler.register(
                localpart=localpart))
            logger.info("Registration based on REST data was successful "
                        "for %s", user_id)
        else:
            logger.info("User %s already exists, registration skipped",
                        user_id)

        defer.returnValue(True)

    @staticmethod
    def parse_config(config):
        return config
