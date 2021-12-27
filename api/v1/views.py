from json import loads
from urllib.parse import urlparse

from flask import request
from flask_restful import Resource

from redis_client import redis_client
from time import time


class VisitedLink(Resource):

    def post(self):
        args = request.get_json(force=True)
        links = args.get('links', [])
        redis_timestamp = int(time())
        domains_list = []
        for link in links:
            domain = urlparse(link).hostname or urlparse(link).path
            if domain and not (domain in domains_list):
                domains_list.append(domain)
        if not domains_list:
            return {'status': 'no content'}, 204
        try:
            redis_client.set(redis_timestamp,
                             str(domains_list).replace("'", '"').encode('utf-8'))
        except Exception as e:
            return {'status': str(e)}, 500
        return {'status': 'ok'}, 201


def create_redis_key_pattern(_from, _to):
    pattern_key = ''
    end_match = False
    for i in range(len(_to)):
        if end_match:
            pattern_key += '?'
        else:
            if _from[i] == _to[i]:
                pattern_key += _to[i]
            else:
                pattern_key += f'[{_from[i]}-{_to[i]}]'
                end_match = True
    return pattern_key


class VisitedDomains(Resource):

    def get(self):
        _from = request.args.get('from')
        _to = request.args.get('to')
        if int(_from) > int(_to):
            _from, _to = _to, _from
        key_pattern = create_redis_key_pattern(_from, _to)
        results = set()
        try:
            for links_id in redis_client.scan_iter(match=key_pattern):
                if int(_from) <= int(links_id) <= int(_to):
                    results.update(loads(redis_client.get(links_id.decode('utf-8'))))
            return {'status': 'ok', 'domains': list(results)}
        except Exception as e:
            return {'status': str(e)}, 500
