import redis
import requests
from settings import REDIS_HOST, REDIS_PORT
from time import sleep, time


class TestVisitedLink:
    POST_URL = 'http://127.0.0.1:5050/visited_links'
    GET_URL = 'http://127.0.0.1:5050/visited_domains?from={}&to={}'

    def test1_post1(self):
        r = requests.post(self.POST_URL, json={
            "links": [
                "https://ya.ru",
                "https://ya.ru?q=123",
                "funbox.ru",
                "https://stackoverflow.com/questions/11828270/how-to-exit-the-vim-editor",
            ]
        })
        assert r.status_code == 201
        sleep(5)

    def test2_post2(self):
        r = requests.post(self.POST_URL, json={
            "links": [
                "https://ya.ru?q=question",
                "https://journal.tinkoff.ru/serial-moscow-vladivostok/",
                "https://immune.mos.ru"
            ]
        })
        assert r.status_code == 201
        sleep(5)

    def test3_post3(self):
        r = requests.post(self.POST_URL, json={
            "links": [
                "https://journal.tinkoff.ru/",
                "https://e.mail.ru/inbox",
            ]
        })
        assert r.status_code == 201

    def test4_post_empty_request(self):
        r = requests.post(self.POST_URL, json={
            "links": [
                "https://",
            ]
        })
        assert r.status_code == 204

    def test5_get_123(self):
        cur_time = int(time())
        r = requests.get(self.GET_URL.format(cur_time - 16, cur_time + 1))
        assert r.status_code == 200
        data = r.json()
        data['domains'].sort()
        assert data == {
            "status": "ok",
            "domains": [
                "e.mail.ru",
                "funbox.ru",
                "immune.mos.ru",
                "journal.tinkoff.ru",
                "stackoverflow.com",
                "ya.ru",
            ]
        }

    def test6_get_12(self):
        cur_time = int(time())
        r = requests.get(self.GET_URL.format(cur_time - 16, cur_time - 2))
        assert r.status_code == 200
        data = r.json()
        data['domains'].sort()
        assert data == {
            "status": "ok",
            "domains": [
                "funbox.ru",
                "immune.mos.ru",
                "journal.tinkoff.ru",
                "stackoverflow.com",
                "ya.ru",
            ]
        }

    def test7_get_3(self):
        cur_time = int(time())
        r = requests.get(self.GET_URL.format(cur_time - 2, cur_time + 1))
        assert r.status_code == 200
        data = r.json()
        data['domains'].sort()
        assert data == {
            "status": "ok",
            "domains": [
                "e.mail.ru",
                "journal.tinkoff.ru"
            ]
        }

    def test8_get_empty(self):
        cur_time = int(time())
        r = requests.get(self.GET_URL.format(cur_time + 1, cur_time + 2))
        assert r.status_code == 200
        assert r.json() == {
            "status": "ok",
            "domains": []
        }
        redis_db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        curr_time = int(time())
        for i in range(curr_time - 16, curr_time + 1):
            redis_db.delete(str(i))
