import logging

import tornado.web
import redis

import config
from tools import hash_password

class RegisterHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("register.html")

    def post(self):
        self.redis_client = redis.Redis(host=config.REDIS_IP_ADDRESS, db=2)
        self.logger = logging.getLogger('websocket')
        login_id = self.get_argument("loginId")
        login_password = self.get_argument("loginPassword")
        redis_key = "users:%s" % login_id
        if self.redis_client.get(redis_key):
            self.finish('{"result": "conflict"}')
            return 
        self.redis_client.set(redis_key, hash_password(login_password))
        self.logger.info("Logging in user %s", login_id)
        self.set_secure_cookie("loginId", login_id)
        self.finish('{"result": "success"}')
