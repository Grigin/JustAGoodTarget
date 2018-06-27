import numpy as np
import gensim
from gensim.models import Word2Vec
from collections import Counter
import requests
import re
from sklearn.decomposition import PCA
from matplotlib import pyplot
import wget
import nltk
from nltk.corpus import stopwords
import pymorphy2
import operator
from rutermextract import TermExtractor
from pymongo import MongoClient


def dell_stopwords(text):
    stop_words = stopwords.words('russian')
    return [w for w in text.split() if w not in stop_words]


def tag_mystem(text, mapping, m):
    text = re.sub(r'[A-z&=;]+', r'', text)
    text = ' '.join(dell_stopwords(text))

    term_extractor = TermExtractor()
    limit = 30
    new_text = ' '.join([term.normalized for term in term_extractor(text, limit)])

    tagged = []
    for w in new_text.split():
        p = morph.parse(w)[0]
        POS = p.tag.POS
        if POS in mapping:
            tagged.append(p.normal_form + '_' + mapping[POS])
        else:
            tagged.append(p.normal_form + '_X')

    return np.array(tagged)


def person_cloud(groups, inter, activ, POS_m, mapping, n_c=0.3):  # текст
    group_tag = []
    for group in groups:
        group_tag += list(tag_mystem(group, mapping, POS_m))

    # sorted_group = sorted(Counter(groups).items(), key=operator.itemgetter(1))
    # group = [i[0] for i in sorted_group[:int(len(groups) * n_c)]]

    inter = tag_mystem(inter, mapping, POS_m)
    activ = tag_mystem(activ, mapping, POS_m)

    cloud_inter = set(inter) | set(activ) | set(group_tag)
    cloud_inter = set(group_tag)
    return cloud_inter


def Group_cloud(key_words, model, lim=100):
    return set(key_words) | set(similar_words(key_words, model))


def dist_by_vector(vector, word, model):
    dist_vec = []
    for w in vector:
        if w in model:
            dist_vec.append(model.wv.distance(word, w))
    return np.mean(np.array(dist_vec))


def similar_words(key_words, model, lim=300):
    if len(key_words) >= lim:
        return key_words
    else:
        len_key_words = len(key_words)
        need = lim - len_key_words
        similar_words = []

        similar_words += [w for w in model.most_similar(key_words, topn=need * 2)]
        similar_words = sorted(Counter([word[0] for word in similar_words]).items(), key=operator.itemgetter(1))[
                        :len(similar_words) // 2]
        similar_words = sorted([(pair[0], dist_by_vector(key_words, pair[0], model)) for pair in similar_words],
                               key=operator.itemgetter(1))[len(similar_words) // 2:]

    return [w[0] for w in similar_words]


def cloud_inter(person_cloud, Group_cloud):
    return len(person_cloud & Group_cloud)


connection = MongoClient("<ds>")
database = connection['grigins_base']
collection = database['AdTargeting']
id = collection.find_one()
key_words = id['keywords']

stop_words = stopwords.words('russian')
mapping = {'NOUN': "NOUN", "ADJF": "ADJ", "ADJS": "ADJ", "COMP": "ADJ", "VERB": "VERB", "INFN": 'VERB', "PRTF": "VERB",
           "PRTS": "VERB", "GRND": "VERB", "NUMR": "NUM", "ADVB": "ADV", "NPRO": "NOUN", "PRED": "ADV", "PREP": "PRON",
           "CONJ": "SCONJ", "PRCL": "PART", "INTJ": "INTJ"}

morph = pymorphy2.MorphAnalyzer()
m = 'ruscorpora_upos_skipgram_300_5_2018.vec'
model = gensim.models.KeyedVectors.load_word2vec_format(m, binary=False)

import json


class TARGET:
    def __init__(self, data, key_words, morph, model, mapping):
        self.morph = morph
        self.model = model
        self.mapping = mapping
        self.discription = tag_mystem(key_words, mapping, morph)
        self.group_cloud = Group_cloud(self.discription, model)
        self.data = data

    def make_target(self):
        scores = dict()
        i = 0
        print('Len of data is {}'.format(len(data)))
        for person in data:
            vk_id = person[0]
            activ, inter = person[1].split('\t')
            lim_group = 20
            groups = [' '.join(d.values()) for d in person[2][1:lim_group]]

            p_cloud = person_cloud(groups, inter, activ, self.morph, self.mapping)
            score = cloud_inter(p_cloud, self.group_cloud)
            scores[vk_id] = score
            i += 1

        scores = sorted(scores.items(), key=operator.itemgetter(1))[::-1]
        print(i, scores)
        return [i[0] for i in scores]


with open("final.txt") as f:
    data = [json.loads(line.strip()) for line in f]


mod = TARGET(data, key_words, morph, model=model, mapping=mapping)
a = mod.make_target()
print(a)
json.dumps(a[:100])
with open('recipients.txt', 'w') as f:
    f.write(json.dumps(a[:20]))

import FinalSend
