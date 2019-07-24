"""
The flask application package.
"""
import logging
import os
from flask import Flask
from applicationinsights.flask.ext import AppInsights

app = Flask(__name__)
app.secret_key = os.environ['FLASK_KEY']
app.config['PREFERRED_URL_SCHEME'] = os.environ['PREFERRED_URL_SCHEME']
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app.config['APPINSIGHTS_INSTRUMENTATIONKEY'] = os.environ['APPINSIGHTS_INSTRUMENTATIONKEY']

# log requests, traces and exceptions to the Application Insights service
appinsights = AppInsights(app)

import BitWebAdmin.views