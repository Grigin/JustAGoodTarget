import random
import tornado.ioloop
import tornado.web
import json
import time
from pymongo import MongoClient

connection = MongoClient("#")
database = connection['#']
collection = database['AdTargeting']
message_collection = database['message']
sleep_collection = database['sleep']

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


    def post(self):
        group_id = self.get_argument("group_id")
        keywords = self.get_argument("keywords")
        collection.insert_one({"group_id": group_id, "keywords": keywords})
        sleep_collection.insert_one({"sleepMode": "True"})
        self.redirect('/success')



class SucessHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('loading.html')

    def post(self):
        message = self.get_argument("message")
        message_collection.insert_one({"message": message})
        self.redirect('/done')

class FinalHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("done.html")



routes = [
    (r"/", MainHandler),
    (r"/success", SucessHandler),
    (r"/done", FinalHandler)
 ]

app = tornado.web.Application(routes, debug=True)
app.listen(80)
tornado.ioloop.IOLoop.current().start()