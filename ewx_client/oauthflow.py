import os
import json
from datetime import datetime
from requests_oauthlib import OAuth2Session

def google_oauth_flow():

    #read secret file google api
    with open('F:\\client_secret_symbolic_bit.apps.googleusercontent.com.json', 'r') as f:
        secret_file = json.load(f)
        secret = secret_file['web']
    
    print('read in super-secret google api credentials.')
    print('')
    
    #run oauth consent
    SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'openid']
    oauth = OAuth2Session(secret['client_id'], redirect_uri=secret['redirect_uris'][0], scope=SCOPES)
    authorization_url, state = oauth.authorization_url('https://accounts.google.com/o/oauth2/auth', access_type="offline", prompt="consent")

    print('Please go to %s and authorize access.' % authorization_url)
    print('')
    
    authorization_response = input('Enter the full callback URL')
    print('')
    
    #get access token
    token = oauth.fetch_token('https://accounts.google.com/o/oauth2/token', authorization_response=authorization_response, client_secret=secret['client_secret'])
    print('fetched extra super-secret token.')
    
    token_exp = datetime.fromtimestamp(token['expires_at'])
    print('Bearer token expires at: {}.'.format(token_exp.strftime('%m/%d/%Y %H:%M:%S')))
    print('')
    
    #write modified client secret
    secret['type'] = 'authorized_user'
    secret['refresh_token'] = token['refresh_token']

    with open('F:\\super-secret-google-shit.json', 'w') as g:
        json.dump(secret, g)
    
    print('wrote new client secret to F:\\super-secret-google-shit.json')
    
    os.environ['JPY_USER'] = "True"
    os.environ['REFRESH_TOKEN'] = secret['refresh_token']
    os.environ['CLIENT_ID'] = secret['client_id']
    os.environ['CLIENT_SECRET'] = secret['client_secret']
    os.environ['TOKEN_URI'] = secret['token_uri']
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'F:\\super-secret-google-shit.json'
    print('set necessary os environment variables.')
    
    return(oauth, secret, token)