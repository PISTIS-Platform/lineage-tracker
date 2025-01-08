# identity_manager.py

import logging

import uuid, requests,json, os
from flask import make_response,jsonify
from functools import lru_cache
from dataclasses import dataclass
import jwt

logger = logging.getLogger('identity_manager')

KEYCLOAK_URL = os.getenv('KEYCLOAK', 'https://auth.pistis-market.eu/auth/realms/PISTIS/protocol/openid-connect/token')
AUTHENTICATION_ID = os.getenv('LINEAGE_TRACKER_ID', 'pistis-test-only')
AUTHENTICATION_SECRET = os.getenv('LINEAGE_TRACKER_SECRET', 'DYuAlXn8kC1SVzFiYgApfjcodZhdxreL')

@dataclass
class IdentityManager():
    content_type: str
    grant_type: str
    permission : str

class IdentityManagerApi():

    # def service_account_authenticate(self,keycloak_object):
        
    #     headers = {
    #         'Content-Type': keycloak_object.content_type
    #     }
    #     keycloak_request = {
    #         'grant_type': keycloak_object.grant_type,
    #         'client_id': AUTHENTICATION_ID,
    #         'client_secret': AUTHENTICATION_SECRET
    #     }

    #     keycloak_response = requests.post(KEYCLOAK_URL, headers=headers, data=keycloak_request)

    #     return keycloak_response
    
    # ##NOTE : Not sure if required
    # def user_account_authenticate(self,keycloak_object):

    #     headers = {
    #         'Content-Type': keycloak_object.content_type
    #     }
    #     keycloak_request = {
    #         'grant_type': keycloak_object.grant_type,
    #         'client_id': AUTHENTICATION_ID,
    #         'client_secret': AUTHENTICATION_SECRET,
    #         'username': "00-test",
    #         'password': "00-test"
    #     }

    #     keycloak_response = requests.post(KEYCLOAK_URL, headers=headers, data=keycloak_request)

    #     return keycloak_response
   
    def user_account_authorize(self, keycloak_object, access_token):
        
        headers = {
            'Content-Type': keycloak_object.content_type,
            'Authorization': f'Bearer {access_token}'
        }
        keycloak_request = {
            'grant_type': keycloak_object.grant_type,
            'audience': 'resource-server'
        }

        # Sending authorization request to keycloak server
        # TODO: Add permission key if dataset id can be checked
        response = requests.post(KEYCLOAK_URL, headers=headers, data=keycloak_request)
        logger.debug("Keycloak response - %s", response)
        logger.debug("Keycloak response text - %s", response.text)
        
        if response.status_code == 200:
            encoded_jwt = response.json()["access_token"]
            # logger.debug("Encoded jwt - %s", encoded_jwt)
            
            # Decode the JWT without verifying the signature
            decoded_jwt = jwt.decode(encoded_jwt, options={"verify_signature": False})
            # logger.debug("Decoded jwt - %s", decoded_jwt)
            # logger.debug("Decoded jwt [authorization] - %s", decoded_jwt['authorization'])
            
            ## TODO: Check for ids in authorization and check if the permission matches 
        
        return response