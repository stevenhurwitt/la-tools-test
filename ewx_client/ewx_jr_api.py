import logging
import os
import socket
import requests
import time
import re
import urllib
from retrying import retry

import httplib2
from googleapiclient import discovery
from oauth2client import GOOGLE_TOKEN_URI
from oauth2client.client import GoogleCredentials, OAuth2Credentials

from energyworx_client.auth import SCOPES
from googleapiclient.errors import HttpError

#from auth import DEFAULT_API_ROOT
from auth.external_service import ExternalService
import parser

#from parser.tags import parse_tags
#from parser.timeseries import parse_result_df, parse_nested_structure_result_df

logger = logging.getLogger()
client_store = dict()

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



class EWX(object):

    def __init__(self, namespace_id=None, api_root=None, credentials=None):
        super(EWX, self).__init__()
        if not namespace_id:
            namespace_id = os.environ.get('EWX_NAMESPACE')
            logger.warning("No namespace parameter could be found, so we are using the primary namespace of the user")
        if not api_root:
            api_root = DEFAULT_API_ROOT
        self.namespace_id = namespace_id
        self.api_root = api_root
        logger.info('Using namespace = %s and api_root = %s', namespace_id, api_root)
        self.client = ExternalService.get_client(api_root=api_root, credentials=credentials)


    def __update_namespace(self, request, async=False):
        request.headers.update({'x-namespace': self.namespace_id})
        if async:
            request.headers.update({'x-async-request': async})
        return request

    def __execute_and_handle_response(self, request, async=False):
        try:
            updated_request = self.__update_namespace(request, async)
        except Exception as ex:
            logger.error('Namespace could not be updated: %s', ex, exc_info=True)
            raise Exception('Namespace could not be updated: {}'.format(ex))
        for count in range(2):
            try:
                return updated_request.execute(num_retries=3)
            except socket.error as socket_error:
                if socket_error.strerror == 'Connection reset by peer':
                    logger.info('%s -> retry', socket_error.strerror)
                    continue
            except HttpError:
                raise
            except Exception as ex:
                logger.error('Request failed: %s', ex, exc_info=True)
                raise Exception('Request failed: {}'.format(ex))


    def get_datasource(self, id):
        """ Gets a datasource by identifier.

        Args:
            id (str): A datasource identifier as a string.

        Returns:
            dict: A datasource dictionary.
        """
        request = self.client.datasource().datasource().get(id=id)
        return self.__execute_and_handle_response(request)

    # Query
    def execute_query(self, query, job_id=None, limit=10, page_token=None, raw_result=False, priority='interactive'):
        """ Execute an EQL query.

        Args:
            query (str): The query as a string.
            job_id (str): if provided, it will try to fetch the result from this job id
            limit (int):
            page_token (str or None):
            raw_result (bool): return raw JSON result from API or parse into dataframe

        Returns:
            str or dict or pd.DataFrame: Results of the query in a dataframe.
        """
        job_complete = False
        while not job_complete:
            request = self.client.query().query().execute(query=query, jobId=job_id, limit=limit, pageToken=page_token, priority=priority)
            result = self.__execute_and_handle_response(request)
            job_complete = result['reference'].get('jobComplete', True)
            job_id = result['reference'].get('jobId')
            time.sleep(0.1)
        if isinstance(result, str) or raw_result:
            return result
        try:
            return parse_result_df(result=result)
        except Exception:
            pass
        try:
            return parse_nested_structure_result_df(result=result)
        except Exception:
            pass
        try:
            return parse_tags(result=result)
        except Exception:
            pass


    def search_files(self, filename=None, tags=None, read_only=None, created_date=None, user_id=None, market_adapter_id=None, limit=None, page_token=None):
        request = self.client.storage().storage().files().search(filename=filename, tags=tags,
                                                                 readOnly=read_only, createdDate=created_date,
                                                                 userId=user_id, marketAdapterId=market_adapter_id,
                                                                 limit=limit, pageToken=page_token)
        return self.__execute_and_handle_response(request)
