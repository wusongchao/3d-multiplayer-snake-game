import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os
import json


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("1.html")


class ChatHandler(tornado.websocket.WebSocketHandler):
    users = set()

    def __init__(self, application, request, **kwargs):
        super(ChatHandler, self).__init__(application, request, **kwargs)
        self.opponent = None
        self.is_playing = False

    def check_origin(self, origin):
        return True

    # noinspection PyBroadException
    def open(self):
        for user in ChatHandler.users:
            if user.opponent is None:
                ChatHandler.users.add(self)
                self.opponent = user
                user.opponent = self
                self.write_message("ready")
                self.opponent.write_message("ready")
                self.is_playing = self.opponent.is_playing = True
                return

        ChatHandler.users.add(self)

    def on_message(self, message):
        # json_object = json.loads(message)

        # if "identity" in json_object:
        #     self.identity = json_object["identity"]
        # else:
        if self.opponent is not None:
            self.opponent.write_message(message)

    def on_close(self):
        if self.is_playing:
            self.opponent.write_message("lose")
            ChatHandler.users.pop(self.opponent)
        else:
            if self.opponent is not None:
                self.opponent.opponent = None

        ChatHandler.users.pop(self)


if __name__ == '__main__':
    app = tornado.web.Application(
        handlers=[
            (r"/", IndexHandler),
            (r"/ws", ChatHandler)
        ],
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=True
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(12345)
    tornado.ioloop.IOLoop.instance().start()
