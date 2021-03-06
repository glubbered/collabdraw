import logging
import uuid
import config
from os.path import join

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.template as template

from org.collabdraw.handler.websockethandler import RealtimeHandler
from org.collabdraw.handler.uploadhandler import UploadHandler
from org.collabdraw.handler.loginhandler import LoginHandler
from org.collabdraw.handler.logouthandler import LogoutHandler
from org.collabdraw.handler.registerhandler import RegisterHandler

logger = logging.getLogger('websocket')
logger.setLevel(logging.INFO)

ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
ch.setLevel(logging.INFO)
logger.addHandler(ch)


class IndexHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        if not config.DEMO_MODE:
            return self.get_secure_cookie("loginId")
        else:
            return True

    @tornado.web.authenticated
    def get(self):
        loader = template.Loader(config.ROOT_DIR)
        return_str = loader.load(join(config.HTML_ROOT, "index.html")).generate(app_ip_address=config.APP_IP_ADDRESS,
                                                        app_port=config.PUBLIC_LISTEN_PORT)
        self.finish(return_str)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/realtime/', RealtimeHandler),
            (r'/resource/(.*)', tornado.web.StaticFileHandler,
             dict(path=config.RESOURCE_DIR)),
            (r'/upload', UploadHandler),
            (r'/login.html', LoginHandler),
            (r'/logout.html', LogoutHandler),
            (r'/register.html', RegisterHandler),
            (r'/index.html', IndexHandler),
            (r'/', IndexHandler),
            (r'/(.*)', tornado.web.StaticFileHandler,
             dict(path=config.ROOT_DIR)),
        ]

        settings = dict(
            auto_reload=True,
            gzip=True,
            login_url="login.html",
            cookie_secret=str(uuid.uuid4()),
        )

        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    if not config.ENABLE_SSL:
        http_server = tornado.httpserver.HTTPServer(Application())
    else:
        http_server = tornado.httpserver.HTTPServer(Application(), ssl_options={
            "certfile": config.SERVER_CERT,
            "keyfile": config.SERVER_KEY,
        })
    logger.info("Listening on port %s" % config.APP_PORT)
    http_server.listen(config.APP_PORT)
    tornado.ioloop.IOLoop.instance().start()
