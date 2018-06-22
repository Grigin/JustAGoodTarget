import vk
from time import time, sleep
from pymongo import MongoClient

connection = MongoClient("mongodb://grigin:57School@ds155631.mlab.com:55631/grigins_base")
database = connection['grigins_base']

message_collection = database['message']
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
    if fm:
        api().messages.send(v=v, user_id=sid, message=mess, forward_messages=fm)
    else:
        api().messages.send(v=v, user_id=sid, message=mess)


session1 = vk.AuthSession('6296592', '89244784789', 'mypass', scope='messages')
api1 = vk.API(session1)
FPS = 21

with open('recipients.txt', 'r') as f:
    ids = [int(x.strip()) for x in f.readlines()]

for id in ids:
    usend(mess=message, sid=id)
    tick(FPS)

