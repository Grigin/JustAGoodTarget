import vk
from time import time, sleep
from pymongo import MongoClient
import json

connection = MongoClient("<ds>")
database = connection['grigins_base']

message_collection = database['message']
messageID = message_collection.find_one()
while messageID is None:
    messageID = message_collection.find_one()
message = messageID['message']


def api():
    return api1


def tick(t):
    t = 1/t
    global lt
    if time() - lt >= t:
        pass
    else:
        sleep(t - (time() - lt))
    lt = time()


def usend(sid, mess, fm=False):
    try:
        if fm:
            api().messages.send(v=5.64, user_id=sid, message=mess, forward_messages=fm)
        else:
            api().messages.send(v=5.64, user_id=sid, message=mess)
    except:
        pass


lt = 0
session1 = vk.AuthSession('appid', 'login', 'password', scope='messages')
api1 = vk.API(session1)
FPS = 21

with open('recipients.txt', 'r') as f:
    ids = json.loads(f.read().strip())

for id in ids:
    usend(mess=message, sid=id)
    tick(FPS)

