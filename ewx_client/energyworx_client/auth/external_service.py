import logging
import os

import httplib2
from googleapiclient import discovery
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client.client import GoogleCredentials, OAuth2Credentials

from energyworx_client.auth import SCOPES

client_store = dict()

logger = logging.getLogger()

MS_TOKEN_URI = 'https://login.microsoftonline.com/common/oauth2/token'
GOOGLE_API = 'googleapis'
AZURE_API = 'microsoftonline'


class ExternalService(object):
    VERSION = 'v1'

    def __init__(self):
        pass

    @staticmethod
    def _get_token_uri(token_uri):
        if GOOGLE_API in token_uri:
            return GOOGLE_TOKEN_URI
        elif AZURE_API in token_uri:
            return MS_TOKEN_URI
        else:
            raise RuntimeError('Unsupported OAuth provider for %s', token_uri)

    @staticmethod
    def _get_credentials(credentials=None):
        """
            Checks environment in order of precedence:
            - Environment variable GOOGLE_APPLICATION_CREDENTIALS pointing to a file with stored credentials information.
            - Google App Engine (production and testing)

        Returns:
            (OAuth2Credentials or GoogleCredentials)
        """
        if not credentials:
            if os.environ.get('JPY_USER'):
                # we are running in datalab, so derive the user credentials from the environment
                # This is required for datalab to work as the user credentials are only set in the environment
                if not os.environ.get('REFRESH_TOKEN') or not os.environ.get("CLIENT_ID") or not os.environ.get("CLIENT_SECRET"):
                    raise RuntimeError("Not all required environment variables are found: REFRESH_TOKEN, CLIENT_ID, CLIENT_SECRET")
                return OAuth2Credentials(
                    access_token=None,
                    client_id=os.environ['CLIENT_ID'],
                    client_secret=os.environ['CLIENT_SECRET'],
                    refresh_token=os.environ['REFRESH_TOKEN'],
                    token_uri=ExternalService._get_token_uri(os.environ['TOKEN_URI']),
                    token_expiry=None,
                    user_agent='Python client library')
            else:
                credentials = GoogleCredentials.get_application_default()
                if credentials.create_scoped_required():
                    credentials = credentials.create_scoped(SCOPES)
                return credentials
        if not credentials:
            raise RuntimeError("Could not find proper credentials!")
        return credentials

    @classmethod
    def get_client(cls, api_root=None, credentials=None, http_timeout=60):
        """

        Args:
            namespace:
            api_root (str):
            credentials (ServiceAccountCredentials):
            namespace (str):
            http_timeout (int):

        Returns:

        """
        logging.debug("Creating {service_name} client".format(service_name=cls.__name__.title()))
        credentials = ExternalService._get_credentials(credentials)
        http = httplib2.Http(disable_ssl_certificate_validation=True, timeout=http_timeout)
        credentials.authorize(http)
        discovery_url = '%s/discovery/v1/apis/ewx/%s/rest' % (api_root+'/_ah/api',  cls.VERSION)
        logging.info("Discovering services using %s", discovery_url)
        service = discovery.build(cls.__name__.lower(), cls.VERSION, discoveryServiceUrl=discovery_url, http=http)
        logging.info("Client created")
        return service

