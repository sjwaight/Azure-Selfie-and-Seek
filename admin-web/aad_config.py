import os, ast

OAUTH_ENABLED = ast.literal_eval(os.environ['OAUTH_ENABLED'])
TENANT = os.environ['AADTENANT']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
AUTHORITY_HOST_URL = "https://login.microsoftonline.com"
AUTHORITY_URL = AUTHORITY_HOST_URL + '/' + TENANT
RESOURCE = "https://graph.windows.net"
TEMPLATE_AUTHZ_URL = ('https://login.microsoftonline.com/{}/oauth2/authorize?' +
                      'response_type=code&client_id={}&redirect_uri={}&' +
                      'state={}&resource={}')