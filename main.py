import logging

from flask import Flask
from flask_restful import Api

import api.v1.views as api_resources
from redis_client import redis_client
from settings import FLASK_PORT, REDIS_URL

app = Flask(__name__)
api = Api(app)

app.config['REDIS_URL'] = REDIS_URL
logging.basicConfig(filename='log.log', level=logging.DEBUG)

api.add_resource(api_resources.VisitedLink, '/visited_links')
api.add_resource(api_resources.VisitedDomains, '/visited_domains')

if __name__ == '__main__':
    redis_client.init_app(app)
    app.run(debug=True, port=FLASK_PORT)
