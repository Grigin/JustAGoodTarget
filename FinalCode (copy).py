import vk
from datetime import date
from collections import deque
import json
from time import time, sleep
from pymongo import MongoClient

connection = MongoClient("<ds>")
database = connection['grigins_base']

collection = database['AdTargeting']
id = collection.find_one()
while id is None:
    id = collection.find_one()
groupId = id["group_id"]

sleepcollection = database['sleep']
sleepID = sleepcollection.find_one()
while sleepID.get('sleepMode') is None:
    sleepID = sleepcollection.find_one()
sleepMode = sleepID["sleepMode"]

print('Starting')

lt = 0
v = 5.64
FPS = 18
now = int(date.today().isoformat().split('-')[0])


def letters(text):
    text = text.lower()
    newt = ''
    text.replace('\n\n', ' ')
    text.replace('\n', ' ')
    for i in text:
        if (ord('а') <= ord(i) <= ord('я')) or i == ' ' or (ord('a') <= ord(i) <= ord('z')):
            newt += i
    return newt


def CheckGroup(id_user):
    offset = 0
    array = []
    try:
        while True:
            resp = api().groups.get(user_id=id_user, offset=offset, v=5.64, fields="description, status", extended=1)
            tick(FPS)
            array += resp["items"]
            offset += 1000
            if offset > resp["count"]:
                break
    except:
        pass
    newarr = []
    for i in array:
        d = dict()
        d['description'] = letters(i.get('description', ''))
        d['name'] = letters(i['name'])
        newarr.append(d)
    return newarr


def get(id_group):
    arr = []
    c = 0
    for i in getMembers(id_group):
        c += 1
        print(c)
        arr += getFriends(i)
    return arr


def getMembers(id_group):
    offset = 0
    array = []

    while True:
        resp = api().groups.getMembers(group_id=id_group, offset=offset, fields="bdate", v=5.64)
        tick(FPS)
        array += resp["items"]
        offset += 1000
        if offset > resp["count"]:
            break
    return [x['id'] for x in array]


def getFriends(id_user):
    offset = 0
    array = []
    minage = 12
    maxage = 20

    fyear, lyear = now - maxage, now - minage
    try:
        while True:
            resp = api().friends.get(user_id=id_user, offset=offset, v=5.64, fields="bdate")
            tick(FPS)
            array += resp["items"]
            offset += 5000
            if offset > resp["count"]:
                break
    except:
        pass
    narr = []
    for person in array:
        if not person.get('bdate') is None:
            bdate = person['bdate'].split('.')
            if len(bdate) == 3:
                year = int(bdate[2])
                if fyear <= year <= lyear:
                    narr.append(person['id'])
            else:
                narr.append(person['id'])
        else:
            narr.append(person['id'])
    return narr


def api():
    global ses
    ans = ses.popleft()
    ses.append(ans)
    return ans


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


session1 = vk.Session(access_token='token1')
api1 = vk.API(session1)
session2 = vk.Session(access_token='token2')
api2 = vk.API(session2)
session3 = vk.Session(access_token='token3')
api3 = vk.API(session3)
session4 = vk.Session(access_token='token4')
api4 = vk.API(session4)
session5 = vk.Session(access_token='token5')
api5 = vk.API(session5)
session6 = vk.Session(access_token='token6')
api6 = vk.API(session6)
ses = deque([api1, api2, api3, api4, api5, api6])

with open('bin.txt', 'w') as f:
    f.write('0')

print('In process')
members = {x:1 for x in getMembers(groupId)}
a = get(groupId)
print(a)
ids = [x for x in a if members.get(x) is None]
print('Got ids')
parts = []

for x in range(len(ids) // 1000 + 1):
    print(x, len(ids) // 1000 + 1, 'getting userinfo')
    parts += api().users.get(user_ids=ids[x*1000:(x+1)*1000], v=5.64, fields='activities, interests')
    tick(FPS)

print(len(parts), len(ids))
with open('info.txt', 'w') as f:
    pass

for user in parts:
    with open('info.txt', 'a') as f:
        f.write(json.dumps([user['id'], user.get('activities', '') + '\t' + user.get('interests', '')]) + '\n')


with open('info3.txt', 'w') as f:
    pass
c = 0
for id in ids:
    c += 1
    print(c, len(ids), 'infogroups')
    with open('info3.txt', 'a') as f:
        f.write(json.dumps([id] + CheckGroup(id)) + '\n')

with open('info.txt', 'r') as f:
    res = [json.loads(x) for x in f.readlines()]

with open('info3.txt', 'r') as f:
    res2 = [json.loads(x) for x in f.readlines()]

with open('final.txt', 'w') as f:
    print(len(res), len(res2))
    for x in range(len(res)):
        res[x].append(res2[x])
        f.write(json.dumps(res[x]) + '\n')

print('Done')
import just_a_good
