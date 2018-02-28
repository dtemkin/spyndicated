# D.Temkin : spyndicated.utils.textproc (v0.3.1-1) - Copyright LGPLv3 (2018)

from collections import Counter
from string import ascii_lowercase, digits, punctuation

import numpy as np
import spacy
from gensim.corpora import Dictionary
from gensim.models import LdaModel

from spyndicated import get_config
from spyndicated.utils.utils import os, find_next_filename

nlp = spacy.load("en")


def stops_list(file="stopwords.lst"):
    stops = open(get_config(filename=file))
    stops_list = [s.lower() for s in stops.readlines()]
    stops_list.extend(list("".join([punctuation, digits, ascii_lowercase])))
    return stops_list


def tags_generator(tokens, ntags=5, **kwargs):
    inclfreq = kwargs.get("incl_freq", False)
    tokens = [x.text.lower().capitalize() for x in tokens if x.tag_ in ["NNP", "NN"]]
    cnt = Counter(tokens)
    if inclfreq is True:
        return cnt.most_common(n=ntags)
    else:
        return [x[0] for x in cnt.most_common(ntags)]


def tokenizer(text_block, stops=[s.lower() for s in stops_list()]):
    doc = nlp(text_block)
    tokens = [x for x in doc if x.text.lower() not in stops]
    return tokens


def doc2bow(doc, **kwargs):
    stops = kwargs.get("stopwords", stops_list())
    tokens = tokenizer(doc, stops=stops)
    return np.array(tokens, dtype=np.str)

